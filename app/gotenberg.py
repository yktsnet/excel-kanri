"""Gotenberg クライアント。LibreOffice ルートで Office ファイルを PDF に変換する。

`convert_to_pdf(src, dest)` のシグネチャは、後続 Issue で
`packages.watch_convert` の変換関数として注入する前提に合わせてある。
"""

from pathlib import Path

import httpx

from app.config import settings


class GotenbergError(RuntimeError):
    """Gotenberg への変換リクエストが失敗した場合に送出する。"""


def convert_to_pdf(src: Path, dest: Path) -> None:
    """src（xlsx 等）を Gotenberg の LibreOffice ルートで pdf に変換し dest に保存する。"""
    url = f"{settings.gotenberg_url.rstrip('/')}/forms/libreoffice/convert"

    with src.open("rb") as f:
        files = {"files": (src.name, f)}
        try:
            response = httpx.post(url, files=files, timeout=60.0)
        except httpx.HTTPError as exc:
            raise GotenbergError(f"Gotenberg への接続に失敗しました: {exc}") from exc

    if response.status_code != 200:
        raise GotenbergError(
            f"Gotenberg が変換に失敗しました (status={response.status_code}): {response.text}"
        )

    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(response.content)
