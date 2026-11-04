"""LaTeX rendering of a table (``booktabs``)."""

from __future__ import annotations

from pyxtdpthresh.extras.reporting.escape import latex, latex_number
from pyxtdpthresh.extras.reporting.table_spec import Cell, TableSpec


def _stars(count: int) -> str:
    """Stars in math mode, as ``$^{***}$``."""
    return f"$^{{{'*' * count}}}$" if count else ""


def _cell(cell: Cell, single_row: bool) -> str:
    """Estimate, stars and, on a single row, the statistic."""
    head = latex_number(cell.text) + _stars(cell.stars)
    if single_row and cell.below:
        head += " " + latex_number(cell.below)
    return head


def render(spec: TableSpec) -> str:
    """Return ``spec`` as a LaTeX ``table`` environment (needs the ``booktabs`` package)."""
    n, width = spec.n_columns, spec.n_columns + 1
    out = [r"\begin{table}[!htbp]", r"\centering"]
    if spec.font_size:
        out.append("\\" + spec.font_size)
    if spec.title:
        out.append(r"\caption{" + latex(spec.title) + "}")
    if spec.label:
        out.append(r"\label{" + spec.label + "}")
    out += [r"\begin{tabular}{l" + "c" * n + "}", r"\toprule"]
    if len(set(spec.dep_vars)) == 1:
        title = f"{latex(spec.dep_var_label)}: {latex(spec.dep_vars[0])}"
        head = rf"\multicolumn{{{n}}}{{c}}{{\textit{{{title}}}}}"
        out += [f" & {head} \\\\", rf"\cmidrule(lr){{2-{width}}}"]
    else:
        out.append(" & ".join(["", *(latex(v) for v in spec.dep_vars)]) + r" \\")
    if any(spec.column_labels):
        out.append(" & ".join(["", *(latex(c) for c in spec.column_labels)]) + r" \\")
    out += [" & ".join(["", *(latex(c) for c in spec.columns)]) + r" \\", r"\midrule"]
    block = None
    for row in spec.rows:
        if row.block and row.block != block:
            out.append(rf"\multicolumn{{{width}}}{{l}}{{\textit{{{latex(row.block)}}}}} \\")
        block = row.block
        cells = [_cell(c, spec.single_row) for c in row.cells]
        out.append(" & ".join([latex(row.label), *cells]) + r" \\")
        if not spec.single_row:
            out.append(" & ".join(["", *(latex_number(c.below) for c in row.cells)]) + r" \\")
    if spec.stats:
        out.append(r"\midrule")
    for stat in spec.stats:
        out.append(
            " & ".join([latex(stat.label), *(latex_number(v) for v in stat.values)]) + r" \\"
        )
    out.append(r"\bottomrule")
    for note in spec.notes:
        out.append(rf"\multicolumn{{{width}}}{{l}}{{\footnotesize {latex_note(note)}}} \\")
    out += [r"\end{tabular}", r"\end{table}"]
    return "\n".join(out) + "\n"


def latex_note(note: str) -> str:
    """Escape a note; the stars of the legend are written in math mode like those of the cells."""
    escaped = latex(note)
    return escaped.replace("***p", "$^{***}$p").replace("**p", "$^{**}$p").replace("*p", "$^{*}$p")
