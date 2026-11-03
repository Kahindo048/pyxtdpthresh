"""Estimation sample and units of ``xtdpthresh``.

Two samples are distinguished, as in the Stata command:

* the **equation sample**: rows that satisfy ``where`` and are complete in the dependent
  variable, the threshold variable and every regressor (including the automatic lag of ``y``);
  only these rows form moment equations;
* the **history sample**: every row of the panel (``history="panel"``) or only the rows that
  satisfy ``where`` (``history="sample"``); rows of the history that are not in the equation
  sample serve as sources of lagged values and instruments.

The data are then arranged by unit, in the column order the estimator uses:
``[L.y (dynamic), x, exogenous, endogenous, predetermined]``.  Units with fewer than two
equation rows cannot form a transformed equation and are dropped.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd

from pyxtdpthresh._errors import DataError
from pyxtdpthresh._i18n import message
from pyxtdpthresh._types import BoolArray, FloatArray, IntArray
from pyxtdpthresh.core.quantiles import mm_quantile
from pyxtdpthresh.data.operators import Term, evaluate
from pyxtdpthresh.data.panel import Panel, build_panel
from pyxtdpthresh.data.sampling import complete_rows, resolve_where
from pyxtdpthresh.models.xtdpthresh.design import Specification

#: Role of each column of ``x``: lag of ``y``, strictly exogenous, endogenous, predetermined.
LAG_Y, EXOGENOUS, ENDOGENOUS, PREDETERMINED = 1, 2, 3, 4
#: Fewest units that can be estimated.
MIN_UNITS = 5


@dataclass(frozen=True)
class XtdpthreshData:
    """Units of the estimation, rows sorted by (unit, time).

    Attributes
    ----------
    spec
        The validated specification.
    unit_labels
        Identifier of each retained unit.
    offsets
        Unit ``i`` owns rows ``offsets[i]:offsets[i + 1]``.
    time
        Integer period of each row.
    y, q
        Dependent and threshold variable at each row.
    x
        ``(n_rows, K)`` regressors; missing values only in rows outside the equation sample.
    names
        Name of each column of ``x``.
    var_type
        Role of each column of ``x`` (:data:`LAG_Y`, :data:`EXOGENOUS`, ...).
    eq
        True for the rows of the equation sample.
    instruments
        ``(n_rows, k_inst)`` external instruments (missing values allowed).
    source_row
        Position of each row in the input frame.
    n_units_dropped
        Units removed for having fewer than two equation rows.
    """

    spec: Specification
    unit_labels: np.ndarray
    offsets: IntArray
    time: IntArray
    y: FloatArray
    q: FloatArray
    x: FloatArray
    names: tuple[str, ...]
    var_type: IntArray
    eq: BoolArray
    instruments: FloatArray
    source_row: IntArray
    n_units_dropped: int

    @property
    def n_units(self) -> int:
        """Number of retained units."""
        return int(self.offsets.size - 1)

    @property
    def n_rows(self) -> int:
        """Number of rows of the history sample of the retained units."""
        return int(self.time.size)

    @property
    def unit_of_row(self) -> IntArray:
        """Index (0-based) of the unit that owns each row."""
        return np.repeat(np.arange(self.n_units, dtype=np.int64), np.diff(self.offsets))


def _fail(key: str, code: int = 498, **fields: Any) -> DataError:
    return DataError(message(key, **fields), stata_code=code, key=key)


def _constant_within(values: FloatArray, groups: IntArray) -> bool:
    """Whether ``values`` is constant in every group with two or more rows (``const_within``)."""
    # Stata: xdpt2_const_within (xtdpthresh.ado:8261); True when fewer than two rows
    if values.shape[0] < 2:
        return True
    order = np.argsort(groups, kind="stable")
    g, v = groups[order], values[order]
    starts = np.flatnonzero(np.r_[True, g[1:] != g[:-1]])
    lows = np.minimum.reduceat(v, starts)
    highs = np.maximum.reduceat(v, starts)
    return bool(np.all(lows == highs))


def _terms_of(spec: Specification) -> list[Term]:
    """Terms in the column order of ``x`` (without the lag of ``y``)."""
    return [*spec.x, *spec.exogenous, *spec.endogenous, *spec.predetermined]


def _check_not_collinear_in_time(
    spec: Specification, columns: FloatArray, eq: BoolArray, panel: Panel
) -> None:
    """Refuse regressors and a threshold that the transformation removes (return code 498)."""
    # Stata: xtdpthresh.ado:1101-1166
    method = spec.options.method
    unit_of_row = panel.unit_of_row[eq]
    time = panel.time[eq]
    names = [t.name for t in _terms_of(spec)]
    for j, name in enumerate(names):
        if _constant_within(columns[eq, j], unit_of_row):
            raise _fail("xd_const_unit", name=name, method=method)
    if spec.options.time_effects:
        for j, name in enumerate(names):
            if _constant_within(columns[eq, j], time):
                raise _fail("xd_const_time", name=name)
    q = panel.column(spec.q)[eq]
    if _constant_within(q, unit_of_row):
        raise _fail("xd_q_const_unit", q=spec.q, method=method)
    if spec.options.time_effects and _constant_within(q, time):
        raise _fail("xd_q_const_time", q=spec.q)


def _check_threshold_support(spec: Specification, q_all: FloatArray, eq: BoolArray,
                             hist: BoolArray) -> None:  # fmt: skip
    """Check that the threshold variable has values and variation (initial trimmed range)."""
    # Stata: xtdpthresh.ado:1238-1265
    usable = q_all[hist & np.isfinite(q_all)]
    if usable.size == 0:
        raise _fail("xd_q_no_values", q=spec.q)
    cut = (spec.options.trim / 2) * 100
    low, high = mm_quantile(usable, cut / 100), mm_quantile(usable, (100 - cut) / 100)
    if low >= high:
        in_equations = q_all[eq]
        if in_equations.size == 0 or float(np.min(in_equations)) >= float(np.max(in_equations)):
            raise _fail("xd_q_no_variation", q=spec.q)


def _unit_columns(spec: Specification, panel: Panel) -> tuple[FloatArray, list[str], IntArray]:
    """Regressors of the full panel in the column order of the estimator."""
    columns, names, kinds = [], [], []
    if spec.lag_of_y is not None:
        columns.append(panel.lag(panel.column(spec.y), 1))
        names.append(spec.lag_of_y.name)
        kinds.append(LAG_Y)
    for role, terms in (
        (EXOGENOUS, (*spec.x, *spec.exogenous)),
        (ENDOGENOUS, spec.endogenous),
        (PREDETERMINED, spec.predetermined),
    ):
        for term in terms:
            columns.append(evaluate(panel, term))
            names.append(term.name)
            kinds.append(role)
    matrix = np.column_stack(columns) if columns else np.empty((panel.n_rows, 0))
    return matrix, names, np.array(kinds, dtype=np.int64)


def prepare_data(
    frame: pd.DataFrame,
    spec: Specification,
    *,
    id: str | None = None,
    time: str | None = None,
    where: str | Sequence[bool] | BoolArray | None = None,
) -> XtdpthreshData:
    """Select the samples and arrange the data by unit.

    Parameters
    ----------
    frame
        Long data, one row per (unit, period).
    spec
        Validated specification, from ``check_specification``.
    id, time
        Identifier and time columns (or index level names).
    where
        Condition selecting the equation sample (and, with ``history="sample"``, the history).

    Raises
    ------
    DataError
        On invalid panel keys (459), no usable observation (2000), a regressor or the
        threshold variable that the transformation removes, an empty threshold range or fewer
        than five usable units (498).
    """
    # Stata: xtdpthresh.ado:1043-1265 (samples, checks), xdpt2_build_units (2587)
    bases = [spec.y, spec.q]
    for term in (*_terms_of(spec), *spec.iv):
        if term.base not in bases:
            bases.append(term.base)
    panel = build_panel(frame, bases, id=id, time=time)
    where_mask = resolve_where(frame, where)[panel.source_row]
    hist = np.ones(panel.n_rows, dtype=np.bool_) if spec.options.history == "panel" else where_mask

    x_full, names, var_type = _unit_columns(spec, panel)
    if spec.lag_of_y is not None and spec.options.history == "sample":
        # a lag whose source row lies outside the history sample is not available
        x_full[:, 0] = np.where(panel.lag(hist.astype(np.float64), 1) == 1.0, x_full[:, 0], np.nan)
    y_all, q_all = panel.column(spec.y), panel.column(spec.q)
    eq = where_mask & complete_rows(np.column_stack([y_all, q_all, x_full]))
    if not eq.any():
        raise DataError(message("no_usable_obs"), stata_code=2000, key="no_usable_obs")

    first_term = 1 if spec.lag_of_y is not None else 0
    _check_not_collinear_in_time(spec, x_full[:, first_term:], eq, panel)
    _check_threshold_support(spec, q_all, eq, hist)

    instruments = (
        np.column_stack([evaluate(panel, t) for t in spec.iv])
        if spec.iv
        else np.empty((panel.n_rows, 0))
    )
    return _arrange_units(spec, panel, hist, eq, x_full, names, var_type, instruments)


def _arrange_units(
    spec: Specification,
    panel: Panel,
    hist: BoolArray,
    eq: BoolArray,
    x_full: FloatArray,
    names: list[str],
    var_type: IntArray,
    instruments: FloatArray,
) -> XtdpthreshData:
    """Keep the history rows of the units that have at least two equation rows."""
    # Stata: xdpt2_build_units (xtdpthresh.ado:2587), then "need >= 5 units"
    unit = panel.unit_of_row
    in_history = hist
    eq_count = np.bincount(unit[eq & in_history], minlength=panel.n_units)
    has_rows = np.bincount(unit[in_history], minlength=panel.n_units) > 0
    keep_unit = eq_count >= 2
    keep = in_history & keep_unit[unit]
    n_retained = int(keep_unit.sum())
    if n_retained < MIN_UNITS:
        raise _fail("xd_few_units", n=n_retained)

    rows = np.flatnonzero(keep)
    kept_units, counts = np.unique(unit[rows], return_counts=True)
    offsets = np.concatenate([[0], np.cumsum(counts)]).astype(np.int64)
    return XtdpthreshData(
        spec=spec,
        unit_labels=panel.unit_labels[kept_units],
        offsets=offsets,
        time=panel.time[rows],
        y=panel.column(spec.y)[rows],
        q=panel.column(spec.q)[rows],
        x=np.ascontiguousarray(x_full[rows]),
        names=tuple(names),
        var_type=var_type,
        eq=eq[rows],
        instruments=np.ascontiguousarray(instruments[rows]),
        source_row=panel.source_row[rows],
        n_units_dropped=int((has_rows & ~keep_unit).sum()),
    )
