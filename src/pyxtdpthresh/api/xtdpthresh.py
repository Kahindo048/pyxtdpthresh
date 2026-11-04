"""``xtdpthresh``: dynamic panel threshold model in first differences or orthogonal deviations."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

import numpy as np
import pandas as pd

from pyxtdpthresh._types import BoolArray, FloatArray
from pyxtdpthresh.models.xtdpthresh.fit import fit_point
from pyxtdpthresh.results.public import XtdpthreshResult

#: Seeds are drawn in the range Stata's ``set seed`` accepts.
_MAX_SEED = 2**31 - 1


def xtdpthresh(
    data: pd.DataFrame,
    y: str,
    x: Sequence[str] | str = (),
    *,
    q: str,
    id: str | None = None,
    time: str | None = None,
    where: str | Sequence[bool] | BoolArray | None = None,
    grid_values: FloatArray | None = None,
    **options: Any,
) -> XtdpthreshResult:
    """Estimate a dynamic panel threshold model (Nguyen and Lai 2026).

    Parameters
    ----------
    data
        Long data, one row per (unit, period); a two-level ``MultiIndex`` (unit, time) replaces
        ``id`` and ``time``.
    y, x, q
        Dependent variable, strictly exogenous regressors and threshold variable.
    id, time
        Identifier and time columns (or index level names).
    where
        Condition selecting the equation sample (a query string or a boolean array).
    grid_values
        Candidate thresholds to use instead of the grid built from ``grid``.
    **options
        Roles of the other variables (``endogenous``, ``predetermined``, ``exogenous``, ``iv``)
        and every option of the Stata command: ``kink``, ``static``, ``method`` (``"fd"`` or
        ``"fod"``), ``collapse``, ``maxlag``, ``grid``, ``trim``, ``refine``, ``n_boot``,
        ``boot_type``, ``grid_ci``, ``seed``, ``level``...  When the bootstrap is on and
        ``seed`` is omitted, a seed is drawn and recorded: ``result.seed`` replays the run.

    Returns
    -------
    XtdpthreshResult
        Estimates, tests and the methods to print, export, plot and predict.

    Raises
    ------
    SpecificationError
        If the call breaks one of the rules of the Stata command (``key`` names the rule and
        ``stata_code`` is its return code).
    DataError
        If the data cannot be used (repeated pairs, missing keys, no usable observation).
    """
    if options.get("bootstrap", True) and options.get("seed") is None:
        options["seed"] = int(np.random.default_rng().integers(1, _MAX_SEED))
    fit = fit_point(
        data, y, x, q=q, id=id, time=time, where=where, grid_values=grid_values, **options
    )
    return XtdpthreshResult(fit)
