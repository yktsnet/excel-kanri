"""ルートB: shared/ の監視。

packages.watch_convert.watching に app.gotenberg.convert_to_pdf を注入する薄い層。
変換先は監視対象と同じディレクトリ・同じファイル名の .pdf（上書き）。
"""

import threading
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from app.gotenberg import convert_to_pdf
from packages.watch_convert import watching


def _convert(path: Path) -> None:
    dest = path.with_suffix(".pdf")
    convert_to_pdf(path, dest)


@contextmanager
def watch_shared(directory: Path) -> Iterator[threading.Event]:
    """directory（shared/）を監視し、Excel 保存を検知したら同名 .pdf に変換する。"""
    with watching(directory, _convert) as stop:
        yield stop
