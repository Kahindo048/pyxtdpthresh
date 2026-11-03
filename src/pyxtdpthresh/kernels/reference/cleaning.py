"""NumPy reference of :func:`pyxtdpthresh.kernels.cleaning.independent_columns`."""

from __future__ import annotations

import numpy as np
from scipy.linalg import solve_triangular

from pyxtdpthresh._types import BoolArray, FloatArray


def independent_columns(gram: FloatArray, tol: float) -> BoolArray:
    """Sequential Cholesky that skips a column whose squared residual is below ``tol``."""
    k = gram.shape[0]
    chol = np.zeros((k, k))
    kept: list[int] = []
    for j in range(k):
        m = len(kept)
        if m == 0:
            ell = np.empty(0)
        else:
            ell = solve_triangular(chol[:m, :m], gram[kept, j], lower=True, check_finite=False)
        pivot = gram[j, j] - float(ell @ ell)
        if pivot >= tol:
            chol[m, :m] = ell
            chol[m, m] = np.sqrt(pivot)
            kept.append(j)
    mask = np.zeros(k, dtype=np.bool_)
    mask[kept] = True
    return mask
