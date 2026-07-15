import threading
from contextlib import contextmanager
from pathlib import Path

import pytest

from packages.watch_convert import cli as cli_module


class _ImmediateInterrupt:
    def wait(self) -> None:
        raise KeyboardInterrupt


def test_main_returns_2_for_missing_directory(tmp_path: Path) -> None:
    exit_code = cli_module.main([str(tmp_path / "missing"), "--exec", "echo {src}"])
    assert exit_code == 2


def test_main_forwards_suffix_and_debounce_and_stops_on_interrupt(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    captured: dict[str, object] = {}

    @contextmanager
    def fake_watching(directory, convert, suffixes, debounce_seconds):
        captured["directory"] = directory
        captured["suffixes"] = suffixes
        captured["debounce_seconds"] = debounce_seconds
        yield threading.Event()

    monkeypatch.setattr(cli_module, "watching", fake_watching)
    monkeypatch.setattr(cli_module.threading, "Event", _ImmediateInterrupt)

    exit_code = cli_module.main(
        [str(tmp_path), "--exec", "echo {src}", "--suffix", ".csv", "--debounce", "2.5"]
    )

    assert exit_code == 0
    assert captured == {
        "directory": tmp_path,
        "suffixes": (".csv",),
        "debounce_seconds": 2.5,
    }


def test_convert_relativizes_path_and_runs_command(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls: list[list[str]] = []
    captured: dict[str, object] = {}

    monkeypatch.setattr(
        cli_module.subprocess, "run", lambda cmd, check: calls.append(cmd)  # noqa: ARG005
    )

    @contextmanager
    def fake_watching(directory, convert, suffixes, debounce_seconds):
        captured["convert"] = convert
        yield threading.Event()

    monkeypatch.setattr(cli_module, "watching", fake_watching)
    monkeypatch.setattr(cli_module.threading, "Event", _ImmediateInterrupt)
    monkeypatch.chdir(tmp_path)

    cli_module.main([str(tmp_path), "--exec", "echo {src}"])

    convert = captured["convert"]
    convert(tmp_path / "a.xlsx")

    assert calls == [["echo", "a.xlsx"]]
