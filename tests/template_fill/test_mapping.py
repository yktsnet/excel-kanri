from pathlib import Path

import pytest

from packages.template_fill import CellRef, MappingError, load_mapping


def write_yaml(tmp_path: Path, content: str) -> Path:
    path = tmp_path / "mapping.yaml"
    path.write_text(content, encoding="utf-8")
    return path


def test_load_mapping_resolves_template_relative_to_file(tmp_path: Path) -> None:
    path = write_yaml(
        tmp_path,
        """
template: templates/form.xlsx
fields:
  name: B3
  room: Sheet2!D5
""",
    )
    mapping = load_mapping(path)
    assert mapping.template == (tmp_path / "templates/form.xlsx").resolve()
    assert mapping.fields["name"] == CellRef(sheet=None, cell="B3")
    assert mapping.fields["room"] == CellRef(sheet="Sheet2", cell="D5")


@pytest.mark.parametrize(
    "content",
    [
        "just a string",
        "fields:\n  name: B3\n",  # template 欠落
        "template: t.xlsx\n",  # fields 欠落
        "template: t.xlsx\nfields: {}\n",  # fields 空
        "template: t.xlsx\nfields:\n  name: 3B\n",  # セル番地不正
        "template: t.xlsx\nfields:\n  name: '!B3'\n",  # シート名空
        "template: t.xlsx\nfields:\n  name: [B3]\n",  # 値が文字列でない
    ],
)
def test_load_mapping_rejects_invalid(tmp_path: Path, content: str) -> None:
    path = write_yaml(tmp_path, content)
    with pytest.raises(MappingError):
        load_mapping(path)


def test_cell_ref_allows_sheet_name_with_space() -> None:
    ref = CellRef.parse("入居 申込!AB12", "field")
    assert ref == CellRef(sheet="入居 申込", cell="AB12")
