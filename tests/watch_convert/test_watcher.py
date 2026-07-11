import time
from pathlib import Path

import pytest

from packages.watch_convert import PendingQueue, is_target, watching


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("form.xlsx", True),
        ("FORM.XLSX", True),
        ("~$form.xlsx", False),  # Office ロックファイル
        (".hidden.xlsx", False),
        ("note.txt", False),
    ],
)
def test_is_target(name: str, expected: bool) -> None:
    assert is_target(Path("/shared") / name, (".xlsx",)) is expected


class FakeClock:
    def __init__(self) -> None:
        self.value = 0.0

    def __call__(self) -> float:
        return self.value


def test_pending_queue_debounces_until_quiet() -> None:
    clock = FakeClock()
    queue = PendingQueue(debounce_seconds=1.0, now=clock)
    path = Path("/shared/a.xlsx")

    queue.mark(path)
    clock.value = 0.5
    assert queue.pop_ready() == []  # まだ静定していない

    queue.mark(path)  # 追加イベントでタイマーがリセットされる
    clock.value = 1.2
    assert queue.pop_ready() == []

    clock.value = 2.5
    assert queue.pop_ready() == [path]
    assert queue.pop_ready() == []  # 取り出し済みは再登場しない


def test_watching_converts_new_file(tmp_path: Path) -> None:
    converted: list[Path] = []

    with watching(tmp_path, converted.append, debounce_seconds=0.2, poll_interval=0.05):
        (tmp_path / "a.xlsx").write_bytes(b"dummy")
        (tmp_path / "~$a.xlsx").write_bytes(b"lock")  # 対象外
        deadline = time.monotonic() + 5.0
        while not converted and time.monotonic() < deadline:
            time.sleep(0.05)

    assert [p.name for p in converted] == ["a.xlsx"]


def test_watching_survives_converter_error(tmp_path: Path) -> None:
    converted: list[Path] = []

    def flaky(path: Path) -> None:
        if path.name == "bad.xlsx":
            raise RuntimeError("boom")
        converted.append(path)

    with watching(tmp_path, flaky, debounce_seconds=0.2, poll_interval=0.05):
        (tmp_path / "bad.xlsx").write_bytes(b"dummy")
        time.sleep(0.5)
        (tmp_path / "good.xlsx").write_bytes(b"dummy")
        deadline = time.monotonic() + 5.0
        while not converted and time.monotonic() < deadline:
            time.sleep(0.05)

    assert [p.name for p in converted] == ["good.xlsx"]


def test_watching_rejects_non_directory(tmp_path: Path) -> None:
    with pytest.raises(ValueError):
        with watching(tmp_path / "missing", lambda p: None):
            pass
