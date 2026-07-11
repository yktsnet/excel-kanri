"""ディレクトリ監視 + デバウンス + 変換関数（注入）の実行。

Excel の保存は短時間に複数のファイルイベントを発生させるため、
最後のイベントから debounce 秒間静かになったファイルだけを変換に回す。
変換処理そのもの（Gotenberg 呼び出し等）はこのモジュールは知らない。
"""

import logging
import threading
import time
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from pathlib import Path

from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer

logger = logging.getLogger(__name__)

Converter = Callable[[Path], None]


def is_target(path: Path, suffixes: tuple[str, ...]) -> bool:
    """変換対象か判定する。Office のロックファイル（~$*）や隠しファイルは除外。"""
    name = path.name
    if name.startswith("~$") or name.startswith("."):
        return False
    return path.suffix.lower() in suffixes


class PendingQueue:
    """イベントを記録し、debounce 秒間イベントが途絶えたパスを取り出すキュー。"""

    def __init__(
        self,
        debounce_seconds: float,
        now: Callable[[], float] = time.monotonic,
    ) -> None:
        self._debounce = debounce_seconds
        self._now = now
        self._pending: dict[Path, float] = {}
        self._lock = threading.Lock()

    def mark(self, path: Path) -> None:
        with self._lock:
            self._pending[path] = self._now()

    def pop_ready(self) -> list[Path]:
        with self._lock:
            cutoff = self._now() - self._debounce
            ready = [p for p, t in self._pending.items() if t <= cutoff]
            for p in ready:
                del self._pending[p]
            return ready


class _Handler(FileSystemEventHandler):
    def __init__(self, queue: PendingQueue, suffixes: tuple[str, ...]) -> None:
        self._queue = queue
        self._suffixes = suffixes

    def _mark(self, raw_path: str | bytes) -> None:
        path = Path(raw_path if isinstance(raw_path, str) else raw_path.decode())
        if is_target(path, self._suffixes):
            self._queue.mark(path)

    def on_created(self, event: FileSystemEvent) -> None:
        if not event.is_directory:
            self._mark(event.src_path)

    def on_modified(self, event: FileSystemEvent) -> None:
        if not event.is_directory:
            self._mark(event.src_path)

    def on_moved(self, event: FileSystemEvent) -> None:
        if not event.is_directory:
            self._mark(event.dest_path)


@contextmanager
def watching(
    directory: Path,
    convert: Converter,
    suffixes: tuple[str, ...] = (".xlsx",),
    debounce_seconds: float = 1.0,
    poll_interval: float = 0.2,
) -> Iterator[threading.Event]:
    """directory を監視し、静定したファイルを convert に渡すワーカーを起動する。

    with ブロックを抜けると監視を停止する。yield される Event を set しても停止できる。
    convert の例外はログに記録し、監視は継続する。
    """
    if not directory.is_dir():
        raise ValueError(f"監視対象がディレクトリではありません: {directory}")

    queue = PendingQueue(debounce_seconds)
    stop = threading.Event()

    observer = Observer()
    observer.schedule(_Handler(queue, suffixes), str(directory), recursive=True)
    observer.start()

    def drain() -> None:
        while not stop.is_set():
            for path in queue.pop_ready():
                try:
                    convert(path)
                except Exception:
                    logger.exception("変換に失敗しました: %s", path)
            stop.wait(poll_interval)

    worker = threading.Thread(target=drain, daemon=True)
    worker.start()

    try:
        yield stop
    finally:
        stop.set()
        observer.stop()
        observer.join()
        worker.join()
