"""Forward orthogonal deviations as triplets (equation row, level observation, weight).

For a unit with equation rows ``e_1 < ... < e_n`` (in time order), the transformed equation at
``e_m`` (``m < n``) is ``c (z_{e_m} - mean(z_{e_{m+1}}, ..., z_{e_n}))`` with
``c = sqrt(T_f / (T_f + 1))`` and ``T_f = n - m`` the number of later equation rows: weight
``c`` on the level at ``e_m`` and ``-c / T_f`` on each later level.  The loop over units is
independent of the data values, so the triplets are written in two passes (count, fill).
"""

from __future__ import annotations

import numpy as np

from pyxtdpthresh._types import BoolArray, FloatArray, IntArray
from pyxtdpthresh.kernels._jit import njit


@njit
def _fod_kernel(
    offsets: IntArray,
    is_equation: BoolArray,
    row: IntArray,
    unit: IntArray,
    ptr: IntArray,
    lev: IntArray,
    weight: FloatArray,
) -> None:
    """Fill the triplets of every unit."""
    n_units = offsets.shape[0] - 1
    longest = 0
    for u in range(n_units):
        longest = max(longest, offsets[u + 1] - offsets[u])
    scratch = np.empty(longest, dtype=np.int64)
    e = 0
    p = 0
    for u in range(n_units):
        n = 0
        for r in range(offsets[u], offsets[u + 1]):
            if is_equation[r]:
                scratch[n] = r
                n += 1
        for m in range(n - 1):
            tf = n - 1 - m
            c = np.sqrt(tf / (tf + 1.0))
            row[e] = scratch[m]
            unit[e] = u
            ptr[e] = p
            lev[p] = scratch[m]
            weight[p] = c
            p += 1
            for k in range(m + 1, n):
                lev[p] = scratch[k]
                weight[p] = -c / tf
                p += 1
            e += 1
    ptr[e] = p


def fod_triplets(
    offsets: IntArray, is_equation: BoolArray
) -> tuple[IntArray, IntArray, IntArray, IntArray, FloatArray]:
    """Equations and triplets of the forward orthogonal deviations.

    Parameters
    ----------
    offsets
        Unit ``i`` owns rows ``offsets[i]:offsets[i + 1]``, sorted by period.
    is_equation
        True for the rows of the equation sample.

    Returns
    -------
    row, unit, pair_ptr, pair_lev, pair_w
        Level row and unit of each equation, and the triplets in compressed-row form.
    """
    off = np.ascontiguousarray(offsets, dtype=np.int64)
    flag = np.ascontiguousarray(is_equation, dtype=np.bool_)
    unit_of_row = np.repeat(np.arange(off.size - 1), np.diff(off))
    rows_of_unit = np.bincount(unit_of_row[flag], minlength=off.size - 1).astype(np.int64)
    n_eq = int(np.sum(np.maximum(rows_of_unit - 1, 0)))
    n_pairs = int(np.sum(np.maximum(rows_of_unit - 1, 0) + rows_of_unit * (rows_of_unit - 1) // 2))
    row = np.empty(n_eq, dtype=np.int64)
    unit = np.empty(n_eq, dtype=np.int64)
    ptr = np.zeros(n_eq + 1, dtype=np.int64)
    lev = np.empty(n_pairs, dtype=np.int64)
    weight = np.empty(n_pairs)
    _fod_kernel(off, flag, row, unit, ptr, lev, weight)
    return row, unit, ptr, lev, weight
