"""Data and instruments of ``xthenreg`` (Seo, Kim and Kim 2019), as the Stata command builds them.

Layout kept from the Mata code: ``y`` and ``q`` are ``(N, T)`` arrays; the regressors are
``x[b]`` with ``b = 0`` the lag of ``y`` (column ``t`` holds ``y_{t-1}``, column 0 is a
placeholder), then the plain regressors, then the ``endogenous()`` ones, then the
``exogenous()`` ones.  Moment conditions are stacked period by period: the equation of period
``t`` (first difference ``y_t - y_{t-1}``) uses a block of instruments made of

* a constant,
* ``y_1 .. y_{t-2}`` (dynamic model only),
* ``dx_t`` for each plain regressor,
* ``x_1 .. x_{t-2}`` for each ``endogenous()`` regressor and ``x_1 .. x_t`` for each
  ``exogenous()`` one (the Stata code gives them two more lags),
* the value at ``t`` of each ``inst()`` variable.

Dynamic equations start at ``t = 3``, static ones at ``t = 2``.
"""

from __future__ import annotations

import warnings
from collections.abc import Sequence
from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy import sparse

from pyxtdpthresh._errors import DataError, PyxdpthreshWarning, SpecificationError
from pyxtdpthresh._i18n import message
from pyxtdpthresh._types import BoolArray, FloatArray, IntArray
from pyxtdpthresh.data.checks import raise_unless_strongly_balanced
from pyxtdpthresh.data.panel import build_panel
from pyxtdpthresh.data.sampling import complete_rows


@dataclass(frozen=True)
class XthenregData:
    """Balanced sample actually used by ``xthenreg``.

    Attributes
    ----------
    unit_labels
        Identifier of each retained unit.
    times
        The ``T`` periods, in increasing order.
    y, q
        ``(N, T)`` arrays.
    x
        ``(k_1, N, T)`` array: lag of ``y``, plain, endogenous, exogenous regressors.
    inst
        ``(k_inst, N, T)`` array of external instruments (``k_inst`` may be 0).
    names
        Names of the regressors ``x[1:]``.
    n_plain, n_endo, n_exo
        Number of plain, ``endogenous()`` and ``exogenous()`` regressors.
    n_units_ignored
        Units dropped because they are not observed in every period of the sample.
    """

    unit_labels: np.ndarray
    times: IntArray
    y: FloatArray
    q: FloatArray
    x: FloatArray
    inst: FloatArray
    names: tuple[str, ...]
    n_plain: int
    n_endo: int
    n_exo: int
    n_units_ignored: int

    @property
    def n_units(self) -> int:
        """Number of units ``N``."""
        return int(self.y.shape[0])

    @property
    def n_periods(self) -> int:
        """Number of periods ``T``."""
        return int(self.y.shape[1])

    @property
    def k_1(self) -> int:
        """Number of regressors including the lag of ``y`` (``k_1`` of the Mata code)."""
        return int(self.x.shape[0])

    @property
    def k_inst(self) -> int:
        """Number of external instruments."""
        return int(self.inst.shape[0])


def prepare_data(
    frame: pd.DataFrame,
    y: str,
    q: str,
    x: Sequence[str] = (),
    endogenous: Sequence[str] = (),
    exogenous: Sequence[str] = (),
    inst: Sequence[str] = (),
    *,
    id: str | None = None,
    time: str | None = None,
    where: str | Sequence[bool] | BoolArray | None = None,
) -> XthenregData:
    """Select the estimation sample and reshape it as ``xthenreg`` does.

    The panel must be strongly balanced (checked on all rows with non-missing keys, as
    ``xtset`` does).  The sample is then the rows satisfying ``where`` and with no missing
    value in ``y``, ``q`` or ``x``; units not observed in every remaining period are dropped
    (``index_non_ms``).

    Raises
    ------
    DataError
        If the panel is not strongly balanced, a variable used outside the sample selection
        has a missing value in the retained rows, or no complete unit remains.
    """
    # Stata: maincode_0719, step 1 (xthenreg.ado:330-409) and index_non_ms (1636)
    sample_vars = [y, q, *x]
    other_vars = [*endogenous, *exogenous]
    columns = [*sample_vars, *other_vars, *inst]
    panel = build_panel(frame, columns, id=id, time=time, where=where)
    if panel.balance_summary is not None:
        raise_unless_strongly_balanced(panel.balance_summary)

    in_sample = complete_rows(panel.columns(sample_vars))
    panel = panel.select(in_sample)
    if panel.n_rows == 0:
        raise DataError(message("no_usable_obs"), stata_code=2000)

    periods = np.unique(panel.time)
    counts = np.diff(panel.offsets)
    complete = counts == periods.size
    n_ignored = int(np.sum(~complete))
    if not complete.any():
        raise DataError(message("no_complete_unit"))
    keep_rows = np.repeat(complete, counts)
    panel = panel.select(keep_rows)

    values = panel.values.reshape(panel.n_units, periods.size, len(columns))
    for name in (*other_vars, *inst):
        if not np.all(np.isfinite(values[:, :, columns.index(name)])):
            raise DataError(message("missing_values", variables=name))
    if np.any(np.diff(periods) != 1):
        warnings.warn(
            "The periods of the sample are not consecutive; xthenreg treats them as if they were.",
            PyxdpthreshWarning,
            stacklevel=2,
        )

    n_units = panel.n_units
    y_mat = values[:, :, 0]
    q_mat = values[:, :, 1]
    others = [values[:, :, j] for j in range(2, 2 + len(x) + len(other_vars))]
    lag_block = np.full((n_units, periods.size), np.nan)
    lag_block[:, 1:] = y_mat[:, :-1]
    x_all = np.stack([lag_block, *others]) if others else lag_block[None]
    first_inst = 2 + len(x) + len(other_vars)
    inst_all = (
        np.stack([values[:, :, first_inst + j] for j in range(len(inst))])
        if inst
        else np.empty((0, n_units, periods.size))
    )
    return XthenregData(
        unit_labels=panel.unit_labels,
        times=periods.astype(np.int64),
        y=np.ascontiguousarray(y_mat),
        q=np.ascontiguousarray(q_mat),
        x=np.ascontiguousarray(x_all),
        inst=np.ascontiguousarray(inst_all),
        names=(*x, *other_vars),
        n_plain=len(x),
        n_endo=len(endogenous),
        n_exo=len(exogenous),
        n_units_ignored=n_ignored,
    )


# ------------------------------------------------------------------------ moment counts
def moment_matrix(n_periods: int, k_1: int, n_endo: int, n_exo: int, k_inst: int = 0) -> IntArray:
    """Count the instruments of each kind in the equation of each period (``moment_mat``).

    Rows are the periods ``t = 2 .. T``.  Columns: constant, lags of ``y``, one per regressor
    (``dx`` for plain ones, a count of levels for ``endogenous()`` and ``exogenous()``), then
    one per external instrument.
    """
    # Stata: moment_mat_con (xthenreg.ado:1317) and maincode_0719 (424-432)
    rows = n_periods - 1
    counts = np.ones((rows, k_1 + 1), dtype=np.int64)
    levels = np.arange(rows, dtype=np.int64)
    counts[:, 1] = levels
    n_lev = n_endo + n_exo
    if n_lev:
        counts[:, k_1 + 1 - n_lev :] = levels[:, None]
    if n_exo:
        counts[:, k_1 + 1 - n_exo :] += 2
    if k_inst:
        counts = np.hstack([counts, np.ones((rows, k_inst), dtype=np.int64)])
    return counts


# --------------------------------------------------------------------------- instruments
@dataclass(frozen=True)
class InstrumentSet:
    """Instruments of every equation, in the row form used by the kernels.

    Attributes
    ----------
    z
        Sparse ``(N * n_eq, L)`` matrix; row ``i * n_eq + p`` is the instrument vector of unit
        ``i`` in its ``p``-th equation, non-zero only in the columns of that equation's block.
    block_sizes
        Number of instruments of each equation (``n_eq`` entries).
    equation_index
        0-based time index ``t`` of each equation (the difference is ``t`` minus ``t - 1``).
    moment_counts
        The ``moment_mat`` of the Stata code, rows ``t = 2 .. T``.
    """

    z: sparse.csr_matrix
    block_sizes: IntArray
    equation_index: IntArray
    moment_counts: IntArray
    n_units: int

    @property
    def n_moments(self) -> int:
        """Number of moment conditions ``L``."""
        return int(self.block_sizes.sum())

    @property
    def n_equations(self) -> int:
        """Number of equation periods."""
        return int(self.block_sizes.size)

    @property
    def block_starts(self) -> IntArray:
        """First column of each equation's block."""
        return np.concatenate([[0], np.cumsum(self.block_sizes)[:-1]]).astype(np.int64)

    @property
    def unit_ptr(self) -> IntArray:
        """Rows of unit ``i`` are ``unit_ptr[i]:unit_ptr[i + 1]``."""
        return (np.arange(self.n_units + 1) * self.n_equations).astype(np.int64)

    def blocks(self) -> list[FloatArray]:
        """Dense ``(N, m_p)`` instruments of each equation, in time order."""
        starts = self.block_starts
        n_eq = self.n_equations
        out = []
        for p in range(n_eq):
            rows = np.arange(self.n_units) * n_eq + p
            block = self.z[rows][:, starts[p] : starts[p] + self.block_sizes[p]]
            out.append(np.asarray(block.toarray()))
        return out

    def literal(self) -> FloatArray:
        """Dense ``(L, N)`` matrix ``Z_mat`` of the Stata code (instruments by unit)."""
        n_eq = self.n_equations
        csr = self.z
        out = np.zeros((self.n_moments, self.n_units))
        starts = self.block_starts
        for p in range(n_eq):
            rows = np.arange(self.n_units) * n_eq + p
            block = csr[rows][:, starts[p] : starts[p] + self.block_sizes[p]].toarray()
            out[starts[p] : starts[p] + self.block_sizes[p], :] = block.T
        return out


def build_instruments(data: XthenregData, static: bool = False) -> InstrumentSet:
    """Instruments of ``xthenreg`` for the dynamic or the static model, with ``inst()``."""
    # Stata: Z_mat_con (xthenreg.ado:896) and Z_mat_IV_add (1454)
    n_units, n_periods = data.n_units, data.n_periods
    first_eq = 2 if static else 3  # first equation period (1-based)
    if n_periods < first_eq:
        raise SpecificationError(
            f"At least {first_eq} periods are needed for the {'static' if static else 'dynamic'} "
            f"model; the sample has {n_periods}."
        )
    k_1 = data.k_1
    moments = moment_matrix(n_periods, k_1, data.n_endo, data.n_exo, data.k_inst)
    n_lev = data.n_endo + data.n_exo
    x_fd = np.diff(data.x, axis=2)  # (k_1, N, T - 1); column kk - 1 is dx at equation index kk

    blocks: list[FloatArray] = []
    equation_index: list[int] = []
    for kk in range(first_eq - 1, n_periods):  # kk = 1-based equation index = 0-based t - 1 + 1
        row = moments[kk - 1]
        parts: list[FloatArray] = [np.ones((n_units, 1))]
        if not static:
            parts.append(data.y[:, : row[1]])  # y_1 .. y_{kk-1}
        for ll in range(3, k_1 + 2):
            b = ll - 2  # index of the regressor block (0 is the lag of y)
            if ll <= k_1 + 1 - n_lev:
                parts.append(x_fd[b, :, kk - 1 : kk])
            else:
                parts.append(data.x[b, :, : row[ll - 1]])
        parts.extend(
            data.inst[j, :, kk : kk + 1] for j in range(data.k_inst)
        )  # value at t = kk + 1
        blocks.append(np.hstack(parts))
        equation_index.append(kk)

    sizes = np.array([b.shape[1] for b in blocks], dtype=np.int64)
    starts = np.concatenate([[0], np.cumsum(sizes)[:-1]])
    n_eq = len(blocks)
    row_idx, col_idx, val = [], [], []
    for p, block in enumerate(blocks):
        m = block.shape[1]
        row_idx.append(np.repeat(np.arange(n_units) * n_eq + p, m))
        col_idx.append(np.tile(starts[p] + np.arange(m), n_units))
        val.append(block.reshape(-1))
    z = sparse.csr_matrix(
        (np.concatenate(val), (np.concatenate(row_idx), np.concatenate(col_idx))),
        shape=(n_units * n_eq, int(sizes.sum())),
    )
    return InstrumentSet(
        z=z,
        block_sizes=sizes,
        equation_index=np.array(equation_index, dtype=np.int64),
        moment_counts=moments,
        n_units=n_units,
    )
