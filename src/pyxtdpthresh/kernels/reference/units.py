"""NumPy reference of :func:`pyxtdpthresh.kernels.units.unit_moments`."""

from __future__ import annotations

import numpy as np
from scipy import sparse

from pyxtdpthresh._types import FloatArray, IntArray


def unit_moments(
    z: FloatArray | sparse.spmatrix, resid: FloatArray, unit_ptr: IntArray
) -> FloatArray:
    """Moments ``g[i, j]``, one unit at a time with dense products."""
    z_dense = sparse.csr_matrix(z, dtype=np.float64).toarray()
    r = np.asarray(resid, dtype=np.float64)
    out = np.zeros((len(unit_ptr) - 1, z_dense.shape[1]))
    for i in range(len(unit_ptr) - 1):
        rows = slice(unit_ptr[i], unit_ptr[i + 1])
        out[i] = z_dense[rows].T @ r[rows]
    return out
