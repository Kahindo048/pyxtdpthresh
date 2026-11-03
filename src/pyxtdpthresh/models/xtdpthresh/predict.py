"""Post-estimation series of ``xtdpthresh``: residuals, fitted values, AR residuals, regime.

Residuals and fitted values are those of the equations the estimator used (first differences, or
forward deviations under ``method="fod"``) on the rows it used; ``ar_residuals`` are the
first-difference residuals the AR tests consume, which differ from the estimation residuals under
``fod``.  All three are missing on rows outside the estimation system (trimmed rows, rows without
an instrument).  ``regime`` is ``1(q > gamma)`` on every row of the frame where ``q`` is observed,
inside or outside the estimation sample.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Literal

import numpy as np
import pandas as pd

from pyxtdpthresh._errors import DataError, SpecificationError
from pyxtdpthresh._i18n import message
from pyxtdpthresh._types import BoolArray, FloatArray, IntArray
from pyxtdpthresh.data.panel import build_panel
from pyxtdpthresh.data.sampling import resolve_where
from pyxtdpthresh.models.xtdpthresh.sample import XtdpthreshData
from pyxtdpthresh.models.xtdpthresh.stack import Stack

Kind = Literal["residuals", "xb", "ar_residuals", "regime"]
KINDS: tuple[str, ...] = ("residuals", "xb", "ar_residuals", "regime")


def _check_frame(
    data: XtdpthreshData, frame: pd.DataFrame, id: str | None, time: str | None
) -> None:
    """Raise unless the keys of the estimation rows are those of the frame (Stata: rc 459)."""
    # Stata: data signature of predict (xtdpthresh_p.ado:132-165); here the keys only
    panel = build_panel(frame, [], id=id, time=time)
    position = np.empty(len(frame), dtype=np.int64)
    position[panel.source_row] = np.arange(panel.source_row.size)
    rows = position[data.source_row]
    unit_of_row = np.repeat(np.arange(panel.n_units), np.diff(panel.offsets))
    same_time = np.array_equal(panel.time[rows], data.time)
    same_unit = np.array_equal(
        np.asarray(panel.unit_labels)[unit_of_row[rows]],
        np.asarray(data.unit_labels)[data.unit_of_row],
    )
    if not (same_time and same_unit):
        raise DataError(message("predict_data_changed"), stata_code=459, key="predict_data_changed")


def _scatter(n: int, source_row: IntArray, rows: IntArray, values: FloatArray) -> FloatArray:
    """Values of the stacked equations placed at the frame position of their row."""
    out = np.full(n, np.nan)
    out[source_row[rows]] = values
    return out


def predict_series(
    kind: str,
    frame: pd.DataFrame,
    *,
    data: XtdpthreshData,
    stack: Stack,
    test_stack: Stack,
    gamma: float,
    theta: FloatArray,
    q: str,
    id: str | None = None,
    time: str | None = None,
    where: str | Sequence[bool] | BoolArray | None = None,
) -> pd.Series:
    """Series of ``kind`` aligned with ``frame`` (missing where it is not defined).

    Parameters
    ----------
    kind
        ``"residuals"``, ``"xb"`` (the fit, ``dy - residual``), ``"ar_residuals"`` or
        ``"regime"``.
    frame
        The data the model was estimated on (same keys).
    data, stack, test_stack
        Prepared data, estimation system and first-difference system of the AR tests.
    gamma, theta
        Estimated threshold and coefficients.
    q
        Threshold variable (for ``regime``).
    id, time
        Identifier and time columns used at estimation.
    where
        Restrict the result to these rows (Stata ``if``).
    """
    # Stata: xtdpthresh_p (xtdpthresh_p.ado:60-200), xdpt2_p_fill (xtdpthresh.ado:8349)
    if kind not in KINDS:
        raise SpecificationError(
            message("predict_kind", kind=kind, options=", ".join(KINDS)),
            stata_code=198,
            key="predict_kind",
        )
    n = len(frame)
    selected = resolve_where(frame, where)
    if kind == "regime":
        values = pd.to_numeric(frame[q], errors="coerce").to_numpy(dtype=np.float64)
        out = np.where(np.isfinite(values), (values > gamma).astype(np.float64), np.nan)
    else:
        _check_frame(data, frame, id, time)
        system = test_stack if kind == "ar_residuals" else stack
        fitted = system.regressors(gamma) @ theta
        resid = system.dy - fitted
        series = {"residuals": resid, "ar_residuals": resid, "xb": system.dy - resid}[kind]
        out = _scatter(n, data.source_row, system.row, series)
    return pd.Series(np.where(selected, out, np.nan), index=frame.index, name=kind)
