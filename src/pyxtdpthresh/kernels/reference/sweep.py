"""NumPy reference of :func:`pyxtdpthresh.kernels.sweep.sweep`."""

from __future__ import annotations

import numpy as np

from pyxtdpthresh._types import BoolArray, FloatArray


def sweep(a: FloatArray, floor: FloatArray) -> tuple[FloatArray, BoolArray]:
    """Generalised inverse by pivoted sweep, one rank-one update per pivot with ``np.outer``."""
    work = np.array(a, dtype=np.float64, copy=True)
    n = work.shape[0]
    dropped = np.zeros(n, dtype=np.bool_)
    pending = np.ones(n, dtype=np.bool_)
    for _ in range(n):
        current = np.where(pending, np.diag(work), -np.inf)
        k = int(np.argmax(current))
        pending[k] = False
        pivot = work[k, k]
        if not pivot > floor[k]:  # also catches NaN
            work[k, :] = 0.0
            work[:, k] = 0.0
            dropped[k] = True
            continue
        row = work[k, :] / pivot
        col = work[:, k].copy()
        col[k] = 0.0
        work -= np.outer(col, row)
        work[k, :] = row
        work[:, k] = -col / pivot
        work[k, k] = 1.0 / pivot
    return (work + work.T) / 2.0, dropped
