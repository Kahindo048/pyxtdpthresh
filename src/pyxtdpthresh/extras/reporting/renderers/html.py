"""HTML rendering of a table (a fragment, with a small style sheet)."""

from __future__ import annotations

from pyxtdpthresh.extras.reporting.escape import web
from pyxtdpthresh.extras.reporting.table_spec import TableSpec

STYLE = (
    "<style>.pyx-table{border-collapse:collapse;font-family:serif;font-size:0.95em}"
    ".pyx-table caption{font-weight:bold;margin-bottom:0.4em}"
    ".pyx-table th,.pyx-table td{padding:0.1em 0.9em;text-align:center}"
    ".pyx-table td:first-child,.pyx-table th:first-child{text-align:left}"
    ".pyx-table thead tr:first-child th{border-top:2px solid #000}"
    ".pyx-table thead tr:last-child th{border-bottom:1px solid #000}"
    ".pyx-table tr.rule td{border-top:1px solid #000}"
    ".pyx-table tfoot td{border-top:2px solid #000;font-size:0.85em;text-align:left}"
    ".pyx-table tr.block td{font-style:italic;text-align:left}</style>"
)


def _td(text: str, colspan: int = 1) -> str:
    span = f' colspan="{colspan}"' if colspan > 1 else ""
    return f"<td{span}>{text}</td>"


def render(spec: TableSpec) -> str:
    """Return ``spec`` as an HTML ``table`` preceded by its style sheet."""
    n, width = spec.n_columns, spec.n_columns + 1
    out = [STYLE, '<table class="pyx-table">']
    if spec.title:
        out.append(f"<caption>{web(spec.title)}</caption>")
    out.append("<thead>")
    if len(set(spec.dep_vars)) == 1:
        head = f"{web(spec.dep_var_label)}: {web(spec.dep_vars[0])}"
        out.append(f'<tr><th></th><th colspan="{n}"><em>{head}</em></th></tr>')
    else:
        out.append("<tr>" + "".join(f"<th>{web(v)}</th>" for v in ("", *spec.dep_vars)) + "</tr>")
    if any(spec.column_labels):
        out.append(
            "<tr>" + "".join(f"<th>{web(c)}</th>" for c in ("", *spec.column_labels)) + "</tr>"
        )
    out.append("<tr>" + "".join(f"<th>{web(c)}</th>" for c in ("", *spec.columns)) + "</tr>")
    out.append("</thead><tbody>")
    block = None
    for row in spec.rows:
        if row.block and row.block != block:
            out.append(f'<tr class="block">{_td(web(row.block), width)}</tr>')
        block = row.block
        first = [
            web(row.label),
            *(_cell(c.text, c.stars, c.below, spec.single_row) for c in row.cells),
        ]
        out.append("<tr>" + "".join(_td(t) for t in first) + "</tr>")
        if not spec.single_row:
            second = ["", *(web(c.below) for c in row.cells)]
            out.append("<tr>" + "".join(_td(t) for t in second) + "</tr>")
    for index, stat in enumerate(spec.stats):
        css = ' class="rule"' if index == 0 else ""
        cells = "".join(_td(web(t)) for t in (stat.label, *stat.values))
        out.append(f"<tr{css}>{cells}</tr>")
    out.append("</tbody>")
    if spec.notes:
        notes = "<br>".join(web(note) for note in spec.notes)
        out.append(f"<tfoot><tr>{_td(notes, width)}</tr></tfoot>")
    out.append("</table>")
    return "\n".join(out) + "\n"


def _cell(text: str, stars: int, below: str, single_row: bool) -> str:
    """Estimate with its stars as superscript, and the statistic when on one row."""
    head = web(text) + (f"<sup>{'*' * stars}</sup>" if stars else "")
    return f"{head} {web(below)}" if single_row and below else head
