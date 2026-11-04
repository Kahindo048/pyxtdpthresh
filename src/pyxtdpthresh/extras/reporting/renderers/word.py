"""Word rendering of a table (needs ``python-docx``): a three-line academic table."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from pyxtdpthresh._errors import PyxdpthreshError
from pyxtdpthresh._i18n import message
from pyxtdpthresh.extras.reporting.table_spec import TableSpec


def _border(cell: Any, edge: str, size: int) -> None:
    """Draw a horizontal rule on one edge (``top`` or ``bottom``) of a table cell."""
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn

    properties = cell._tc.get_or_add_tcPr()
    borders = properties.find(qn("w:tcBorders"))
    if borders is None:
        borders = OxmlElement("w:tcBorders")
        properties.append(borders)
    element = OxmlElement(f"w:{edge}")
    element.set(qn("w:val"), "single")
    element.set(qn("w:sz"), str(size))
    element.set(qn("w:color"), "000000")
    borders.append(element)


def write(spec: TableSpec, path: Path) -> Path:
    """Write ``spec`` to a ``.docx`` file and return the path."""
    try:
        from docx import Document
        from docx.enum.text import WD_ALIGN_PARAGRAPH
        from docx.shared import Pt
    except ImportError as error:  # pragma: no cover - depends on the environment
        raise PyxdpthreshError(
            message(
                "table_missing_package",
                package="python-docx",
                format="Word",
                command="pip install pyxtdpthresh[export]",
            ),
            key="table_missing_package",
        ) from error
    document = Document()
    if spec.title:
        document.add_paragraph(spec.title).runs[0].bold = True
    rows = spec.lines()
    n_notes = len(spec.notes)
    body = rows[: len(rows) - n_notes] if n_notes else rows
    table = document.add_table(rows=len(body), cols=spec.n_columns + 1)
    header_end = 2 + bool(any(spec.column_labels))
    first_stat = len(body) - len(spec.stats)
    for r, row in enumerate(body):
        for c, text in enumerate(row):
            cell = table.cell(r, c)
            paragraph = cell.paragraphs[0]
            run = paragraph.add_run(text)
            run.font.size = Pt(9)
            run.bold = r == header_end - 1
            if c:
                paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
            if r == 0:
                _border(cell, "top", 12)
            if r == header_end - 1:
                _border(cell, "bottom", 6)
            if spec.stats and r == first_stat:
                _border(cell, "top", 6)
            if r == len(body) - 1:
                _border(cell, "bottom", 12)
    for note in spec.notes:
        paragraph = document.add_paragraph()
        paragraph.add_run(note).font.size = Pt(8)
    document.save(str(path))
    return path
