"""NumPy reference of :func:`pyxtdpthresh.kernels.transforms.fod_triplets`."""

from __future__ import annotations

import numpy as np

from pyxtdpthresh._types import BoolArray, FloatArray, IntArray


def fod_triplets(
    offsets: IntArray, is_equation: BoolArray
) -> tuple[IntArray, IntArray, IntArray, IntArray, FloatArray]:
    """Triplets of the forward orthogonal deviations, one list per equation."""
    rows: list[int] = []
    units: list[int] = []
    ptr = [0]
    lev: list[int] = []
    weight: list[float] = []
    for u in range(len(offsets) - 1):
        eq_rows = np.flatnonzero(is_equation[offsets[u] : offsets[u + 1]]) + offsets[u]
        n = eq_rows.size
        for m in range(n - 1):
            later = eq_rows[m + 1 :]
            c = np.sqrt(later.size / (later.size + 1.0))
            rows.append(int(eq_rows[m]))
            units.append(u)
            lev += [int(eq_rows[m]), *map(int, later)]
            weight += [c, *([-c / later.size] * later.size)]
            ptr.append(len(lev))
    return (
        np.array(rows, dtype=np.int64),
        np.array(units, dtype=np.int64),
        np.array(ptr, dtype=np.int64),
        np.array(lev, dtype=np.int64),
        np.array(weight, dtype=np.float64),
    )
