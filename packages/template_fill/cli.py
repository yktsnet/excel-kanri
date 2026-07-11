"""CLI: マッピング YAML + データ JSON から xlsx を生成する。

使用例:
    python -m packages.template_fill mapping.yaml data.json -o out.xlsx
"""

import argparse
import json
import sys
from pathlib import Path

from .fill import FillError, fill_template
from .mapping import MappingError, load_mapping


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="template_fill",
        description="YAML マッピングに従いテンプレート Excel に値を流し込む",
    )
    parser.add_argument("mapping", type=Path, help="マッピング YAML のパス")
    parser.add_argument("data", type=Path, help="入力データ JSON のパス（- で標準入力）")
    parser.add_argument("-o", "--output", type=Path, required=True, help="出力 xlsx のパス")
    args = parser.parse_args(argv)

    try:
        if str(args.data) == "-":
            data = json.load(sys.stdin)
        else:
            data = json.loads(args.data.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise FillError("データ JSON のルートはオブジェクトである必要があります")
        mapping = load_mapping(args.mapping)
        output = fill_template(mapping, data, args.output)
    except (MappingError, FillError, OSError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    print(output)
    return 0
