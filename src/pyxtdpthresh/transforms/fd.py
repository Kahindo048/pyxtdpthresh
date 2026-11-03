"""First-difference equations, as triplets (equation row, level observation, weight).

An equation of unit ``i`` at period ``t`` is formed when the unit has rows at ``t`` and
``t - 1`` (the calendar period, so a gap in the dates gives no equation) and both belong to the
equation sample and are complete in ``y``, ``q`` and the regressors.  The transformed equation
is ``y_t - y_{t-1}`` on the differenced regressors, so it touches two *level* observations with
weights ``+1`` and ``-1``.  Writing the equations this way (rather than forming the differenced
matrices) lets the regime terms, which depend on the threshold through the level observations
only, be accumulated for every candidate threshold in one pass over the levels.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from pyxtdpthresh._types import BoolArray, FloatArray, IntArray
from pyxtdpthresh.core.calendar import row_at_shift


@dataclass(frozen=True)
class FDEquations:
    """First-difference equations of the retained units.

    Attributes
    ----------
    row
        Level row ``t`` of each equation, ordered by unit then period.
    prev
        Level row ``t - 1`` of each equation.
    unit
        Unit of each equation.
    time
        Period ``t`` of each equation.
    unit_ptr
        Unit ``i`` owns the equations ``unit_ptr[i]:unit_ptr[i + 1]`` (empty for a unit with none).
    pair_ptr, pair_lev, pair_w
        Triplets: equation ``e`` is ``sum_k pair_w[k] * level[pair_lev[k]]`` over
        ``k in pair_ptr[e]:pair_ptr[e + 1]`` (here ``+1`` at ``t`` and ``-1`` at ``t - 1``).
    """

    row: IntArray
    prev: IntArray
    unit: IntArray
    time: IntArray
    unit_ptr: IntArray
    pair_ptr: IntArray
    pair_lev: IntArray
    pair_w: FloatArray

    @property
    def n_equations(self) -> int:
        """Number of transformed equations."""
        return int(self.row.size)

    @property
    def n_active_units(self) -> int:
        """Units with at least one equation."""
        return int(np.count_nonzero(np.diff(self.unit_ptr)))


def previous_period_row(offsets: IntArray, time: IntArray) -> IntArray:
    """Row of the same unit one period earlier, ``-1`` where the unit has no such row.

    Parameters
    ----------
    offsets
        Unit ``i`` owns rows ``offsets[i]:offsets[i + 1]``, sorted by period within the unit.
    time
        Integer period of each row.
    """
    return row_at_shift(offsets, time, 1)


def fd_equations(
    offsets: IntArray,
    time: IntArray,
    eq: BoolArray,
    y: FloatArray,
    q: FloatArray,
    x: FloatArray,
) -> FDEquations:
    """Form the first-difference equations of the units.

    A candidate row is skipped when it or its predecessor is outside the equation sample, or
    when ``y``, ``q`` or a regressor is missing at either of them.
    """
    # Stata: xdpt2_transform_unit, method "fd" (xtdpthresh.ado:2862-2880)
    prev = previous_period_row(offsets, time)
    row = np.arange(time.size, dtype=np.int64)
    candidate = (prev >= 0) & eq
    p = np.maximum(prev, 0)
    complete = np.isfinite(y) & np.isfinite(q) & np.all(np.isfinite(x), axis=1)
    valid = candidate & eq[p] & complete & complete[p]

    n_units = offsets.size - 1
    unit_of_row = np.repeat(np.arange(n_units, dtype=np.int64), np.diff(offsets))
    rows = row[valid]
    counts = np.bincount(unit_of_row[valid], minlength=n_units)
    m = rows.size
    lev = np.empty(2 * m, dtype=np.int64)
    lev[0::2] = rows
    lev[1::2] = prev[valid]
    return FDEquations(
        row=rows,
        prev=prev[valid],
        unit=unit_of_row[valid],
        time=time[valid],
        unit_ptr=np.concatenate([[0], np.cumsum(counts)]).astype(np.int64),
        pair_ptr=np.arange(0, 2 * m + 1, 2, dtype=np.int64),
        pair_lev=lev,
        pair_w=np.tile([1.0, -1.0], m),
    )
