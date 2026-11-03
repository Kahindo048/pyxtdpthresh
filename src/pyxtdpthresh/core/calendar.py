"""Calendar lookups inside units: the row of the same unit at another period."""

from __future__ import annotations

import numpy as np

from pyxtdpthresh._types import IntArray


def row_at_shift(
    offsets: IntArray, time: IntArray, shift: int, rows: IntArray | None = None
) -> IntArray:
    """Row of the same unit at period ``time - shift``, ``-1`` where the unit has no such row.

    The period is looked up on the calendar, not by row position, so a gap in the dates gives
    ``-1``; a row of another unit is never returned.

    Parameters
    ----------
    offsets
        Unit ``i`` owns rows ``offsets[i]:offsets[i + 1]``, sorted by period within the unit.
    time
        Integer period of each row.
    shift
        Lag in periods (positive: earlier rows; negative: later rows).
    rows
        Rows to look up; every row when omitted.
    """
    # Stata: xdpt2_find_t(u, u.t[j] - shift) (xtdpthresh.ado:2703)
    n = time.size
    wanted = np.arange(n, dtype=np.int64) if rows is None else np.asarray(rows, dtype=np.int64)
    if n == 0 or wanted.size == 0:
        return np.full(wanted.size, -1, dtype=np.int64)
    unit = np.repeat(np.arange(offsets.size - 1, dtype=np.int64), np.diff(offsets))
    pad = abs(int(shift)) + 1  # spare periods so a lookup never lands in another unit
    t0 = int(np.min(time))
    span = int(np.max(time)) - t0 + 2 * pad + 1
    key = unit * span + (time - t0 + pad)
    target = key[wanted] - shift
    pos = np.searchsorted(key, target)
    clipped = np.minimum(pos, n - 1)
    found = (pos < n) & (key[clipped] == target)
    return np.where(found, clipped, -1).astype(np.int64)
