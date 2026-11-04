"""CSV rendering of a table (the cells as text, stars after the estimate)."""

from __future__ import annotations

import csv
import io

from pyxtdpthresh.extras.reporting.table_spec import TableSpec


def render(spec: TableSpec) -> str:
    """Return ``spec`` as CSV text, one table row per line."""
    buffer = io.StringIO()
    csv.writer(buffer, lineterminator="\n").writerows(spec.lines())
    return buffer.getvalue()
