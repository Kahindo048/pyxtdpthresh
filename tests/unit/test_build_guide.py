"""The PDF of the user guide and the methodological note are built from their sources."""

import shutil
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools import build_guide_pdf as tool  # noqa: E402

TABLE = """\
| Name | Stata | Notes |
|---|---|---|
| `a` | `b` | a long note that takes most of the room of the table |
| `c` | `d` | short |
"""


def test_the_hand_written_list_of_contents_is_dropped():
    text = "**Contents**\n\n1. [One](#one)\n2. [Two](#two)\n\nBody.\n"
    assert tool.strip_contents(text) == "Body.\n"
    assert tool.strip_contents("no list\n") == "no list\n"


def test_a_hatted_gamma_becomes_one_private_character():
    out = tool.hatted_gamma("threshold γ̂ and γ")
    assert tool.PRIVATE_CHARACTER in out and "̂" not in out and out.endswith("γ")


def test_table_columns_get_dashes_in_proportion_to_their_text():
    out = tool.weight_tables(TABLE).split("\n")
    widths = [len(cell) for cell in out[1].strip("|").split("|")]
    assert widths[2] > widths[0] and widths[2] > widths[1]  # the notes column is the widest
    assert out[0] == TABLE.split("\n")[0] and out[2:4] == TABLE.split("\n")[2:4]  # rows are intact


def test_alignment_marks_of_a_table_are_kept():
    table = "| A | B |\n|:---|---:|\n| 1 | 2 |\n"
    separator = tool.weight_tables(table).split("\n")[1]
    assert separator.startswith("|:") and separator.endswith(":|")


def test_the_note_has_the_include_line_of_the_inventory_exactly_once():
    lines = tool.NOTE.read_text(encoding="utf-8").split("\n")
    assert lines.count(tool.INCLUDE_PORTED) == 1


@pytest.mark.slow
@pytest.mark.skipif(
    shutil.which("pandoc") is None or shutil.which("xelatex") is None,
    reason="pandoc and xelatex are needed",
)
def test_the_guide_builds_with_the_note_as_appendix(tmp_path):
    pdf = tool.build(tmp_path / "guide.pdf")
    tex = (tmp_path / "guide.tex").read_text(encoding="utf-8")
    assert pdf.stat().st_size > 50_000
    assert r"\appendix" in tex and "Methodological note" in tex
    assert r"xdpt2\_grid\_search" in tex  # the generated inventory is in the appendix
    assert tex.count(r"\end{document}") == 1
