"""Cholesky that skips dependent columns: which columns of a Gram matrix are independent.

Columns are visited in order; column ``j`` is kept when its squared residual after the kept
earlier columns, ``G[j, j] - l'l`` with ``L l = G[kept, j]``, is at least ``tol``.  The rule is
sequential (a dropped column changes what the later ones are compared with) and costs
``O(k m^2)`` for ``k`` columns and ``m`` kept, so it is a compiled loop.
"""

from __future__ import annotations

import numpy as np

from pyxtdpthresh._types import BoolArray, FloatArray
from pyxtdpthresh.kernels._jit import njit


@njit
def _independent_kernel(gram: FloatArray, tol: float, kept: BoolArray) -> None:
    """Flag in ``kept`` the independent columns of the unit-diagonal Gram matrix ``gram``."""
    k = gram.shape[0]
    chol = np.zeros((k, k))
    index = np.empty(k, dtype=np.int64)
    ell = np.empty(k)
    m = 0
    for j in range(k):
        norm = 0.0
        for a in range(m):
            s = gram[index[a], j]
            for b in range(a):
                s -= chol[a, b] * ell[b]
            ell[a] = s / chol[a, a]
            norm += ell[a] * ell[a]
        pivot = gram[j, j] - norm
        if pivot >= tol:
            for a in range(m):
                chol[m, a] = ell[a]
            chol[m, m] = np.sqrt(pivot)
            index[m] = j
            kept[j] = True
            m += 1


def independent_columns(gram: FloatArray, tol: float) -> BoolArray:
    """Mask of the columns kept by the sequential Cholesky rule.

    Parameters
    ----------
    gram
        Symmetric ``(k, k)`` Gram matrix scaled to a unit diagonal.
    tol
        Smallest squared residual a column needs to be kept.
    """
    work = np.ascontiguousarray(gram, dtype=np.float64)
    if work.ndim != 2 or work.shape[0] != work.shape[1]:
        raise ValueError("gram must be square")
    kept = np.zeros(work.shape[0], dtype=np.bool_)
    _independent_kernel(work, float(tol), kept)
    return kept
