"""マッピング YAML の読み込み・検証。

YAML スキーマ:

    template: templates/example.xlsx   # マッピングファイルからの相対パス
    fields:
      field_name: B3                   # セル番地。"Sheet2!B3" でシート指定
"""

import re
from dataclasses import dataclass
from pathlib import Path

import yaml

CELL_PATTERN = re.compile(r"^[A-Z]{1,3}[1-9][0-9]*$")


class MappingError(ValueError):
    """マッピング YAML が不正な場合に送出する。"""


@dataclass(frozen=True)
class CellRef:
    sheet: str | None
    cell: str

    @classmethod
    def parse(cls, raw: str, field: str) -> "CellRef":
        sheet: str | None = None
        cell = raw
        if "!" in raw:
            sheet, cell = raw.rsplit("!", 1)
            if not sheet:
                raise MappingError(f"フィールド '{field}': シート名が空です: '{raw}'")
        if not CELL_PATTERN.match(cell):
            raise MappingError(
                f"フィールド '{field}': セル番地が不正です: '{raw}'（例: B3, Sheet2!D5）"
            )
        return cls(sheet=sheet, cell=cell)


@dataclass(frozen=True)
class TemplateMapping:
    template: Path
    fields: dict[str, CellRef]


def load_mapping(path: Path) -> TemplateMapping:
    """マッピング YAML を読み込み検証する。template はファイル位置からの相対で解決する。"""
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise MappingError(f"YAML を解析できません: {path}: {exc}") from exc

    if not isinstance(raw, dict):
        raise MappingError(f"マッピングのルートは辞書である必要があります: {path}")

    template = raw.get("template")
    if not isinstance(template, str) or not template:
        raise MappingError(f"'template' キー（テンプレートへの相対パス）が必要です: {path}")

    fields_raw = raw.get("fields")
    if not isinstance(fields_raw, dict) or not fields_raw:
        raise MappingError(f"'fields' キー（フィールド名 → セル番地）が必要です: {path}")

    fields: dict[str, CellRef] = {}
    for name, ref in fields_raw.items():
        if not isinstance(name, str) or not isinstance(ref, str):
            raise MappingError(
                f"fields の項目は文字列 → 文字列である必要があります: {name!r}: {ref!r}"
            )
        fields[name] = CellRef.parse(ref, name)

    return TemplateMapping(template=(path.parent / template).resolve(), fields=fields)
