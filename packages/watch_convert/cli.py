"""CLI: ディレクトリを監視し、静定したファイルごとにコマンドを実行する。

使用例:
    python -m packages.watch_convert shared/ --exec 'echo converted: {src}'

`{src}` が変換対象ファイルの絶対パスに置換される。
"""

import argparse
import logging
import shlex
import subprocess
import threading
from pathlib import Path

from .watcher import watching


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="watch_convert",
        description="ディレクトリを監視し、変更が静定したファイルごとにコマンドを実行する",
    )
    parser.add_argument("directory", type=Path, help="監視するディレクトリ")
    parser.add_argument(
        "--exec",
        dest="command",
        required=True,
        help="実行するコマンド。{src} が対象ファイルのパスに置換される",
    )
    parser.add_argument(
        "--suffix",
        action="append",
        default=None,
        help="対象拡張子（既定: .xlsx。複数指定可）",
    )
    parser.add_argument(
        "--debounce",
        type=float,
        default=1.0,
        help="最終イベントからの静定待ち秒数（既定: 1.0）",
    )
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    suffixes = tuple(args.suffix) if args.suffix else (".xlsx",)

    def convert(path: Path) -> None:
        cmd = [part.replace("{src}", str(path)) for part in shlex.split(args.command)]
        logging.info("実行: %s", shlex.join(cmd))
        subprocess.run(cmd, check=True)

    try:
        with watching(
            args.directory.resolve(),
            convert,
            suffixes=suffixes,
            debounce_seconds=args.debounce,
        ):
            logging.info("監視中: %s（%s / Ctrl+C で終了）", args.directory, " ".join(suffixes))
            threading.Event().wait()
    except KeyboardInterrupt:
        return 0
    except ValueError as exc:
        print(f"error: {exc}")
        return 2
    return 0
