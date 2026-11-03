"""Forward orthogonal deviations of the equation rows, as triplets.

The transformed equation of unit ``i`` at an equation row ``t`` that is followed by at least one
more equation row is ``c (y_t - mean of the later equation rows)`` with
``c = sqrt(T_f / (T_f + 1))`` (``T_f`` the number of later equation rows), and the same for
every regressor.  Only equation rows take part and history-only rows never do.  A gap in the
dates is irrelevant: the future is the later equation rows of the unit, whatever their dates.
The last equation row of a unit has no transformed equation.
"""

from __future__ import annotations

import numpy as np

from pyxtdpthresh._types import BoolArray, FloatArray, IntArray
from pyxtdpthresh.kernels.transforms import fod_triplets
from pyxtdpthresh.transforms.fd import FDEquations


def fod_equations(
    offsets: IntArray,
    time: IntArray,
    eq: BoolArray,
    y: FloatArray,
    q: FloatArray,
    x: FloatArray,
) -> FDEquations:
    """Forward-orthogonal equations of the units (``prev`` is ``-1``: there is no lag row).

    A row takes part when it is in the equation sample and ``y``, ``q`` and the regressors are
    present; the equation sample is already complete, the test only guards direct calls.
    """
    # Stata: xdpt2_transform_unit, method "fod" (xtdpthresh.ado:2881-2905)
    complete = np.isfinite(y) & np.isfinite(q) & np.all(np.isfinite(x), axis=1)
    row, unit, ptr, lev, weight = fod_triplets(offsets, eq & complete)
    n_units = offsets.size - 1
    counts = np.bincount(unit, minlength=n_units)
    return FDEquations(
        row=row,
        prev=np.full(row.size, -1, dtype=np.int64),
        unit=unit,
        time=time[row],
        unit_ptr=np.concatenate([[0], np.cumsum(counts)]).astype(np.int64),
        pair_ptr=ptr,
        pair_lev=lev,
        pair_w=weight,
    )


__all__: list[str] = ["fod_equations"]
