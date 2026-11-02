"""NumPy reference of :func:`pyxtdpthresh.kernels.moments.regime_moments`.

Written as the formula reads, one grid point at a time, with the indicator applied before the
sum: this is also the "literal" evaluation that mirrors the Mata code of ``xthenreg``.
"""

from __future__ import annotations

import numpy as np
from scipy import sparse

from pyxtdpthresh._types import FloatArray, IntArray


def regime_moments(
    z: FloatArray | sparse.spmatrix,
    pair_ptr: IntArray,
    pair_lev: IntArray,
    pair_w: FloatArray,
    w_level: FloatArray,
    q_level: FloatArray,
    grid: FloatArray,
) -> FloatArray:
    """Regime moments ``S[g, j, k]``, evaluated grid point by grid point."""
    z_dense = sparse.csr_matrix(z, dtype=np.float64).toarray()
    n_eq = z_dense.shape[0]
    pair_eq = np.repeat(np.arange(n_eq), np.diff(pair_ptr))
    w_pairs = np.asarray(w_level, dtype=np.float64)[pair_lev]
    q_pairs = np.asarray(q_level, dtype=np.float64)[pair_lev]
    out = np.zeros((len(grid), z_dense.shape[1], w_pairs.shape[1]))
    for g, gamma in enumerate(grid):
        above = (q_pairs > gamma).astype(np.float64)  # NaN compares False
        contribution = np.zeros((n_eq, w_pairs.shape[1]))
        np.add.at(contribution, pair_eq, (pair_w * above)[:, None] * w_pairs)
        out[g] = z_dense.T @ contribution
    return out
