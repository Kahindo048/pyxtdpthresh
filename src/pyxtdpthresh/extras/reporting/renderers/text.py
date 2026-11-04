"""Plain-text rendering of a table (monospaced columns, as on a console)."""

from __future__ import annotations

import sys

from pyxtdpthresh.extras.reporting.table_spec import TableSpec

#: How the Greek letters of the labels are written on a console that cannot show them.
_ASCII = (("γ̂", "gamma-hat"), ("γ", "gamma"), ("δ", "delta"), ("−", "-"))


def _printable(text: str) -> str:
    """Replace the characters the standard output cannot encode (a Windows console)."""
    encoding = getattr(sys.stdout, "encoding", None) or "utf-8"
    try:
        text.encode(encoding)
    except UnicodeEncodeError:
        for char, name in _ASCII:
            text = text.replace(char, name)
    return text


def render(spec: TableSpec) -> str:
    """Return ``spec`` as aligned text with rules, the label column on the left."""
    lines = spec.lines()
    n_notes = len(spec.notes)
    body = lines[: len(lines) - n_notes] if n_notes else lines
    spanning = len(set(spec.dep_vars)) == 1
    sized = body[1:] if spanning else body
    widths = [max(len(row[j]) for row in sized) for j in range(spec.n_columns + 1)]
    total = sum(widths) + 2 * spec.n_columns
    rule, double = "-" * total, "=" * total
    first_stat = len(body) - len(spec.stats)
    header = 1 + bool(any(spec.column_labels)) + 1
    out = [double]
    for index, row in enumerate(body):
        cells = [
            row[0].ljust(widths[0]),
            *(c.center(w) for c, w in zip(row[1:], widths[1:], strict=True)),
        ]
        line = "  ".join(cells).rstrip()
        if len(set(spec.dep_vars)) == 1 and index == 0:
            line = row[0]
        out.append(line)
        if index == header - 1 or (spec.stats and index == first_stat - 1):
            out.append(rule)
    out.append(double)
    out.extend(row[0] for row in lines[len(body) :])
    return _printable("\n".join(out) + "\n")
