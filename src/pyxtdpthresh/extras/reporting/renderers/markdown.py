"""Markdown rendering of a table (a pipe table)."""

from __future__ import annotations

from pyxtdpthresh.extras.reporting.escape import markdown
from pyxtdpthresh.extras.reporting.table_spec import Cell, TableSpec


def _row(cells: list[str]) -> str:
    return "| " + " | ".join(cells) + " |"


def _star_text(text: str, stars: int) -> str:
    """Estimate followed by its stars, escaped so they are not read as emphasis."""
    return markdown(text) + (r"\*" * stars)


def _single(cell: Cell) -> str:
    """Estimate, stars and statistic on one line."""
    line = _star_text(cell.text, cell.stars)
    return f"{line} {markdown(cell.below)}" if cell.below else line


def _header(spec: TableSpec) -> list[str]:
    """Column headers: the name, with the group label and the dependent variable when needed."""
    heads = []
    for index, name in enumerate(spec.columns):
        parts = [markdown(name)]
        if any(spec.column_labels):
            parts.insert(0, markdown(spec.column_labels[index]))
        if len(set(spec.dep_vars)) > 1:
            parts.append(markdown(spec.dep_vars[index]))
        heads.append("<br>".join(p for p in parts if p))
    return ["", *heads]


def render(spec: TableSpec) -> str:
    """Return ``spec`` as a Markdown table with the title and notes around it."""
    n = spec.n_columns
    out: list[str] = []
    if spec.title:
        out += [f"**{markdown(spec.title)}**", ""]
    if len(set(spec.dep_vars)) == 1:
        out += [f"*{markdown(spec.dep_var_label)}: {markdown(spec.dep_vars[0])}*", ""]
    out += [_row(_header(spec)), _row(["---", *[":---:"] * n])]
    block = None
    for row in spec.rows:
        if row.block and row.block != block:
            out.append(_row([f"*{markdown(row.block)}*", *[""] * n]))
        block = row.block
        if spec.single_row:
            out.append(_row([markdown(row.label), *(_single(c) for c in row.cells)]))
            continue
        out.append(_row([markdown(row.label), *(_star_text(c.text, c.stars) for c in row.cells)]))
        out.append(_row(["", *(markdown(c.below) for c in row.cells)]))
    for stat in spec.stats:
        out.append(_row([markdown(stat.label), *(markdown(v) for v in stat.values)]))
    if spec.notes:
        out += ["", *(f"*{markdown(note)}*  " for note in spec.notes)]
    return "\n".join(out) + "\n"
