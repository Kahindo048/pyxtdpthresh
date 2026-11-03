"""Instrument matrix of the first-difference moment equations.

Every equation (unit ``i``, period ``t``) has its own block of instruments, as in Arellano and
Bond (1991): the period constant, the levels ``y_{t-2}, y_{t-3}, ...`` of the dependent variable,
the first difference of each strictly exogenous regressor, the levels of the endogenous
regressors from ``t - 2`` and of the predetermined ones from ``t - 1``, and the external
instruments ``iv()`` dated ``t``.  ``maxlag(lo hi)`` bounds the lags, ``collapse`` replaces the
block-diagonal layout by one shared block (one column per lag instead of one per lag and
period), and ``iv_collapse`` does the same for the external instruments only.

Column order inside a block: constant, lags of ``y``, exogenous differences, then for each
endogenous variable its lags, then for each predetermined variable its lags.  The external
instruments follow all blocks.  The estimates do not depend on the column order; it is kept
identical to the Stata command so that the matrices can be compared entry by entry.

The matrix does not depend on the threshold.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from pyxtdpthresh._errors import DataError
from pyxtdpthresh._i18n import message
from pyxtdpthresh._types import BoolArray, FloatArray, IntArray
from pyxtdpthresh.core.calendar import row_at_shift

#: Roles of the regressor columns (same codes as ``models.xtdpthresh.sample``).
LAG_Y, EXOGENOUS, ENDOGENOUS, PREDETERMINED = 1, 2, 3, 4
#: Largest instrument matrix allocated before empty columns are removed (columns, cells).
MAX_COLUMNS, MAX_CELLS = 5000, 50_000_000


@dataclass(frozen=True)
class InstrumentSettings:
    """Options that shape the instrument set.

    Attributes
    ----------
    lag_lo, lag_hi
        ``maxlag(lo hi)``; ``lag_hi`` may be infinite.  The effective first lag is at least 2
        for ``y`` and the endogenous variables and at least 1 for the predetermined ones.
    collapse
        One shared block of internal instruments instead of one block per period.
    iv_collapse
        One column per external instrument instead of one per instrument and period.
    static
        No lagged dependent variable, hence no instruments built on ``y``.
    method
        ``"fd"`` or ``"fod"``.  With forward orthogonal deviations the lags are counted from
        ``t + 1`` (the transformed error involves later periods) and the first period of the data
        has a block of its own.
    """

    lag_lo: int = 1
    lag_hi: float = math.inf
    collapse: bool = False
    iv_collapse: bool = False
    static: bool = False
    method: str = "fd"


@dataclass(frozen=True)
class InstrumentLayout:
    """Dimensions of the instrument matrix."""

    n_blocks: int
    block_width: int
    core_cols: int
    n_cols: int
    lag_max: int
    lag_lo_y: int
    lag_lo_p: int
    n_lag_y: int
    n_lag_p: int


@dataclass(frozen=True)
class RawInstruments:
    """Instruments before cleaning, for the equations that have at least one.

    Attributes
    ----------
    z
        ``(n_kept, n_cols)`` matrix.
    keep
        True for the equations that have an instrument (they are the rows of ``z``).
    layout
        Dimensions of the matrix.
    col_block
        Block (observed equation period, 0-based) of each column; ``-1`` for a column shared
        by all periods.
    """

    z: FloatArray
    keep: BoolArray
    layout: InstrumentLayout
    col_block: IntArray


def make_layout(
    settings: InstrumentSettings,
    *,
    n_blocks: int,
    span: int,
    k_exog: int,
    k_endog: int,
    k_predet: int,
    k_inst: int,
) -> InstrumentLayout:
    """Dimensions of the instrument matrix.

    Parameters
    ----------
    n_blocks
        Number of observed equation periods that have a block.
    span
        Last equation period minus the first period of the data; no lag is longer.
    k_exog, k_endog, k_predet, k_inst
        Numbers of exogenous, endogenous and predetermined regressor columns and of external
        instruments.
    """
    # Stata: xdpt2_transform_unit (xtdpthresh.ado:2931-2981)
    lag_max = span if settings.lag_hi >= span else int(settings.lag_hi)
    lag_lo_y = max(settings.lag_lo, 2)
    lag_lo_p = max(settings.lag_lo, 1)
    n_lag_y = lag_max - lag_lo_y + 1 if lag_max >= lag_lo_y else 0
    n_lag_p = lag_max - lag_lo_p + 1 if lag_max >= lag_lo_p else 0
    width = 1 + k_exog + k_endog * n_lag_y + k_predet * n_lag_p
    if not settings.static:
        width += n_lag_y
    n_blocks = max(n_blocks, 1)
    core = width if settings.collapse else n_blocks * width
    tail = 0 if k_inst == 0 else (k_inst if settings.iv_collapse else n_blocks * k_inst)
    return InstrumentLayout(
        n_blocks, width, core, core + tail, lag_max, lag_lo_y, lag_lo_p, n_lag_y, n_lag_p
    )


def observed_periods(time: IntArray, eq: BoolArray) -> IntArray:
    """Sorted distinct periods of the equation rows (the periods that have an instrument block)."""
    # Stata: xdpt_teq (xtdpthresh.ado:8666-8674)
    return np.unique(time[eq])


class _Fill:
    """Writes instrument values into ``z`` and records which equations have one."""

    def __init__(
        self, z: FloatArray, available: BoolArray, base: IntArray, usable: BoolArray
    ) -> None:
        self.z, self.available, self.base, self.usable = z, available, base, usable

    def put(self, source_rows: IntArray, values: FloatArray, column_offset: int) -> None:
        """Set ``z[i, base[i] + column_offset]`` where the source row exists and has a value."""
        ok = self.usable & (source_rows >= 0)
        ok[ok] = np.isfinite(values[ok])
        index = np.flatnonzero(ok)
        self.z[index, self.base[index] + column_offset] = values[index]
        self.available[index] = True


def build_instruments(
    *,
    offsets: IntArray,
    time: IntArray,
    eq: BoolArray,
    y: FloatArray,
    x: FloatArray,
    var_type: IntArray,
    inst: FloatArray,
    eq_row: IntArray,
    eq_time: IntArray,
    d_exog: FloatArray,
    settings: InstrumentSettings,
) -> RawInstruments:
    """Instruments of the transformed equations (first differences or forward deviations).

    Parameters
    ----------
    offsets, time, eq
        Rows of the retained units, sorted by (unit, period), and the equation-sample flag.
    y, x
        Dependent variable and regressors at every row (history rows included).
    var_type
        Role of each column of ``x``.
    inst
        External instruments at every row.
    eq_row, eq_time
        Level row and period of each first-difference equation.
    d_exog
        Transformed exogenous regressors at each equation, ``(n_eq, k_exog)``.
    settings
        Instrument options.
    """
    # Stata: xdpt2_transform_unit (xtdpthresh.ado:2931-3095)
    fod_shift = int(settings.method == "fod")
    n_eq = eq_row.size
    periods = observed_periods(time, eq)
    t_min = int(np.min(time[offsets[:-1]])) if offsets.size > 1 else 0
    t_max = int(periods[-1]) if periods.size else t_min
    first_block = int(np.searchsorted(periods, t_min + (0 if fod_shift else 1)))
    k_inst = inst.shape[1]
    layout = make_layout(
        settings,
        n_blocks=periods.size - first_block,
        span=t_max - t_min,
        k_exog=int(np.sum(var_type == EXOGENOUS)),
        k_endog=int(np.sum(var_type == ENDOGENOUS)),
        k_predet=int(np.sum(var_type == PREDETERMINED)),
        k_inst=k_inst,
    )

    if layout.n_cols > MAX_COLUMNS or int(eq.sum()) * layout.n_cols > MAX_CELLS:
        # Stata: projected instrument allocation is unsafe (xtdpthresh.ado:8714)
        raise DataError(
            message(
                "xd_iv_alloc",
                cols=layout.n_cols,
                cells=int(eq.sum()) * layout.n_cols,
                span=t_max - t_min,
            ),
            stata_code=498,
            key="xd_iv_alloc",
        )
    rank = np.searchsorted(periods, eq_time) - first_block
    usable = (rank >= 0) & (rank < layout.n_blocks)
    base = np.zeros(n_eq, dtype=np.int64) if settings.collapse else rank * layout.block_width
    z = np.zeros((n_eq, layout.n_cols))
    available = np.zeros(n_eq, dtype=bool)
    fill = _Fill(z, available, base, usable)

    lag_rows: dict[int, IntArray] = {}

    def at_lag(lag: int) -> IntArray:
        if lag not in lag_rows:
            lag_rows[lag] = row_at_shift(offsets, time, lag - fod_shift, eq_row)
        return lag_rows[lag]

    offset = 1  # column 0 of the block is the constant, written once the rows are chosen
    if not settings.static:
        for j in range(layout.n_lag_y):
            rows = at_lag(layout.lag_lo_y + j)
            fill.put(rows, y[np.maximum(rows, 0)], offset + j)
        offset += layout.n_lag_y

    for column in range(d_exog.shape[1]):
        # the first difference of an exogenous regressor is always present on its own equation
        z[usable, base[usable] + offset + column] = d_exog[usable, column]
        available |= usable
    offset += int(d_exog.shape[1])

    for kind, first, count in (
        (ENDOGENOUS, layout.lag_lo_y, layout.n_lag_y),
        (PREDETERMINED, layout.lag_lo_p, layout.n_lag_p),
    ):
        for source in np.flatnonzero(var_type == kind):
            for j in range(count):
                rows = at_lag(first + j)
                fill.put(rows, x[np.maximum(rows, 0), source], offset + j)
            offset += count

    if k_inst:
        shared = layout.core_cols
        own = np.arange(n_eq, dtype=np.int64)
        base_iv = np.full(n_eq, shared) if settings.iv_collapse else shared + rank * k_inst
        iv_fill = _Fill(z, available, base_iv, usable)
        for j in range(k_inst):
            iv_fill.put(own, inst[eq_row, j], j)

    base_kept = base[available]
    z = z[available]
    z[np.arange(z.shape[0]), base_kept] = 1.0
    return RawInstruments(z, available, layout, _column_blocks(layout, k_inst, settings))


def _column_blocks(layout: InstrumentLayout, k_inst: int, settings: InstrumentSettings) -> IntArray:
    """Block (period) of each column of the matrix, ``-1`` for a column shared by all periods."""
    if settings.collapse:
        core = np.full(layout.core_cols, -1, dtype=np.int64)
    else:
        core = np.repeat(np.arange(layout.n_blocks, dtype=np.int64), layout.block_width)
    if k_inst == 0:
        return core
    if settings.iv_collapse:
        tail = np.full(k_inst, -1, dtype=np.int64)
    else:
        tail = np.repeat(np.arange(layout.n_blocks, dtype=np.int64), k_inst)
    return np.concatenate([core, tail])


#: Former name, kept for the code written before forward deviations were added.
build_fd_instruments = build_instruments
