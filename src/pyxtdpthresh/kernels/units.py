"""Moment contributions of each unit, ``g_i = sum over the rows of unit i of Z[e, :] * resid[e]``.

The matrix of moments ``G`` (units by instruments) is all that the weight matrix, the
variance, the Hansen statistic and the wild bootstrap need.  The kernel reads ``Z`` in
compressed-row form, so no ``(rows * L)`` product is ever formed and zero blocks cost
nothing; units are independent and run in parallel.
"""

from __future__ import annotations

import numpy as np
from scipy import sparse

from pyxtdpthresh._types import FloatArray, IntArray
from pyxtdpthresh.kernels._jit import apply_threads, pjit, prange


@pjit
def _unit_moments_kernel(
    z_ptr: IntArray,
    z_col: IntArray,
    z_val: FloatArray,
    resid: FloatArray,
    unit_ptr: IntArray,
    out: FloatArray,
) -> None:
    """Accumulate ``out[i, :]`` for every unit ``i``."""
    for i in prange(unit_ptr.shape[0] - 1):
        for e in range(unit_ptr[i], unit_ptr[i + 1]):
            r = resid[e]
            for idx in range(z_ptr[e], z_ptr[e + 1]):
                out[i, z_col[idx]] += r * z_val[idx]


def unit_moments(
    z: FloatArray | sparse.spmatrix, resid: FloatArray, unit_ptr: IntArray
) -> FloatArray:
    """Moments ``g[i, j] = sum_{e in unit i} Z[e, j] * resid[e]``.

    Parameters
    ----------
    z
        Instruments of the equation rows, ``(n_eq, L)``, dense or scipy sparse.
    resid
        Value multiplying each equation row, ``(n_eq,)`` (a residual, or the transformed
        dependent variable).
    unit_ptr
        Unit ``i`` owns the equation rows ``unit_ptr[i]:unit_ptr[i + 1]`` (rows sorted by unit).

    Returns
    -------
    numpy.ndarray
        ``(n_units, L)`` array.
    """
    apply_threads()
    z_csr = sparse.csr_matrix(z, dtype=np.float64)
    ptr = np.ascontiguousarray(unit_ptr, dtype=np.int64)
    values = np.ascontiguousarray(resid, dtype=np.float64)
    if values.shape != (z_csr.shape[0],) or ptr[-1] != z_csr.shape[0]:
        raise ValueError("resid and unit_ptr must cover exactly the rows of z")
    if ptr[0] != 0 or np.any(np.diff(ptr) < 0):
        raise ValueError("unit_ptr must start at 0 and not decrease")
    out = np.zeros((ptr.size - 1, z_csr.shape[1]))
    _unit_moments_kernel(
        z_csr.indptr.astype(np.int64), z_csr.indices.astype(np.int64), z_csr.data, values, ptr, out
    )
    return out
