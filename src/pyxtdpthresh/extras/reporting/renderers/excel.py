"""Excel rendering of a table (needs ``openpyxl``)."""

from __future__ import annotations

from pathlib import Path

from pyxtdpthresh._errors import PyxdpthreshError
from pyxtdpthresh._i18n import message
from pyxtdpthresh.extras.reporting.table_spec import TableSpec


def write(spec: TableSpec, path: Path) -> Path:
    """Write ``spec`` to an ``.xlsx`` file with the rules of a journal table; return the path."""
    try:
        from openpyxl import Workbook
        from openpyxl.styles import Alignment, Border, Font, Side
    except ImportError as error:  # pragma: no cover - depends on the environment
        raise PyxdpthreshError(
            message(
                "table_missing_package",
                package="openpyxl",
                format="Excel",
                command="pip install pyxtdpthresh[export]",
            ),
            key="table_missing_package",
        ) from error
    book = Workbook()
    sheet = book.active
    assert sheet is not None
    rows = spec.lines()
    n_notes = len(spec.notes)
    body = rows[: len(rows) - n_notes] if n_notes else rows
    for row in rows:
        sheet.append(row)
    thin, thick = Side(style="thin"), Side(style="medium")
    width = spec.n_columns + 1
    header_end = 2 + bool(any(spec.column_labels))
    first_stat = len(body) - len(spec.stats) + 1
    for column in range(1, width + 1):
        sheet.cell(1, column).border = Border(top=thick)
        sheet.cell(header_end, column).border = Border(bottom=thin)
        if spec.stats:
            sheet.cell(first_stat, column).border = Border(top=thin)
        sheet.cell(len(body), column).border = Border(
            bottom=thick, top=sheet.cell(len(body), column).border.top
        )
    for line in range(1, header_end + 1):
        for column in range(1, width + 1):
            sheet.cell(line, column).font = Font(bold=line == header_end)
    for line in range(1, len(rows) + 1):
        for column in range(2, width + 1):
            sheet.cell(line, column).alignment = Alignment(horizontal="center")
    sheet.column_dimensions["A"].width = max(len(str(r[0])) for r in body) + 2
    for column in range(2, width + 1):
        sheet.column_dimensions[chr(64 + column)].width = 14
    if spec.title:
        sheet.title = spec.title[:31]
    book.save(path)
    return path
