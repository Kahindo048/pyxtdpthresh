"""Point estimation of ``xtdpthresh`` from a data frame: specification to threshold and estimates.

This chains the validated steps: :func:`check_specification`, :func:`prepare_data`,
:func:`build_stack` and :func:`search_threshold`, and issues the warnings of the Stata
command (wide instrument sets, ``refine`` not applied or incomplete) unless ``warn=False``.
Inference (bootstraps, tests, joint variance) is added on top of this result by later blocks.
"""

from __future__ import annotations

import math
import warnings
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd

from pyxtdpthresh._errors import PyxdpthreshWarning
from pyxtdpthresh._i18n import message
from pyxtdpthresh._types import BoolArray, FloatArray
from pyxtdpthresh.instruments.builder import observed_periods
from pyxtdpthresh.kernels._jit import blas_threads
from pyxtdpthresh.models.xtdpthresh.bootstrap import BootstrapResults, run_bootstrap
from pyxtdpthresh.models.xtdpthresh.coefficients import (
    UpperRegime,
    coefficient_names,
    upper_regime,
)
from pyxtdpthresh.models.xtdpthresh.design import Specification, check_specification
from pyxtdpthresh.models.xtdpthresh.diagnostics import (
    HansenTest,
    SerialTests,
    hansen_test,
    serial_tests,
)
from pyxtdpthresh.models.xtdpthresh.predict import predict_series
from pyxtdpthresh.models.xtdpthresh.sample import XtdpthreshData, prepare_data
from pyxtdpthresh.models.xtdpthresh.search import (
    SearchResult,
    search_threshold,
    threshold_support,
)
from pyxtdpthresh.models.xtdpthresh.stack import Stack, build_stack
from pyxtdpthresh.models.xtdpthresh.variance import MIN_Q_VALUES, VarianceFit, final_variance

#: Projected number of instrument columns above which a note, and then a warning, is issued.
NOTE_COLUMNS, WARN_COLUMNS = 300, 1500


@dataclass(frozen=True)
class PointFit:
    """Point estimates of one fit, with the objects that produced them.

    Attributes
    ----------
    spec, data, stack, search
        Validated specification, prepared data, first-difference system and search result.
    variance
        Reported variance (joint with the threshold when available) and its conditional version.
    hansen
        Over-identification test.
    serial
        AR(1) and AR(2) tests.
    n_switch
        Units whose regime changes within their equations at the threshold (``e(N_switch)``).
    id, time
        Identifier and time columns given at estimation (``None`` for the index levels).
    bootstrap
        Bootstrap inference (confidence set of the threshold, tests); ``None`` without it.
    """

    spec: Specification
    data: XtdpthreshData
    stack: Stack
    search: SearchResult
    variance: VarianceFit
    hansen: HansenTest
    serial: SerialTests
    n_switch: int
    id: str | None = None
    time: str | None = None
    bootstrap: BootstrapResults | None = None

    @property
    def n_obs(self) -> int:
        """Stacked equations (``e(N)``)."""
        return self.stack.n_rows

    @property
    def n_instruments(self) -> int:
        """Instruments after cleaning (``e(N_iv)``)."""
        return self.stack.n_instruments

    @property
    def n_units(self) -> int:
        """Units that contribute equations (``e(N_units)``)."""
        return self.stack.n_units

    @property
    def cov(self) -> FloatArray:
        """Variance of the coefficients that is reported (``e(V)``)."""
        return self.variance.cov

    @property
    def names(self) -> tuple[str, ...]:
        """Coefficient names, ``lower:x``, ``change:_cons`` and ``change:x``."""
        return coefficient_names(self.stack.names, kink=self.stack.kink, q=self.spec.q)

    @property
    def scalars(self) -> dict[str, float]:
        """Scalars of the fit under the names of Stata's ``e()`` (``nan`` when missing)."""
        # Stata: ereturn scalars (xtdpthresh.ado:2009-2158)
        fit, search, var = self.search.fit, self.search, self.variance
        cleaned = self.stack.instruments
        ar1, ar2 = self.serial.ar1, self.serial.ar2
        values: dict[str, float] = {
            "N": self.n_obs,
            "N_units": self.n_units,
            "N_clust": self.n_units,
            "N_switch": self.n_switch,
            "N_iv": self.n_instruments,
            "N_iv_common": cleaned.n_common,
            "N_iv_dep": cleaned.n_dependent,
            "N_iv_dep_near": cleaned.dep_near,
            "iv_dep_res": cleaned.dep_res,
            "W1_fallback": self.stack.first_weight.fallback,
            "gamma": fit.gamma,
            "obj": fit.obj,
            "estimator_twostep": fit.twostep,
            "level": self.spec.options.level,
            "q_lo": search.q_lo,
            "q_hi": search.q_hi,
            "grid_admitted": search.grid_admitted,
            "kink_refined": search.kink_refined if self.stack.kink else math.nan,
            "hansen": self.hansen.statistic,
            "hansen_df": self.hansen.df,
            "hansen_p": self.hansen.p_value,
            "ar1": ar1.statistic,
            "ar1_p": ar1.p_value,
            "ar2": ar2.statistic,
            "ar2_p": ar2.p_value,
            "ar_joint": self.serial.joint,
            "ar1_cond": self.serial.ar1_cond.statistic,
            "ar2_cond": self.serial.ar2_cond.statistic,
            "ar1_b0": ar1.b0,
            "ar1_T1": ar1.t1,
            "ar1_TT": ar1.tt,
            "ar2_b0": ar2.b0,
            "ar2_T1": ar2.t1,
            "ar2_TT": ar2.tt,
            "joint_vce": var.joint,
            "gamma_bw": var.bandwidth,
            "q_nvals_bw": var.q_nvals_bw,
            "vce_applied": var.wind_applied,
            "wind_same_threshold": var.same_threshold,
        }
        values.update(self._bootstrap_scalars())
        return {name: float(value) for name, value in values.items()}

    def _bootstrap_scalars(self) -> dict[str, float]:
        """Scalars of the bootstraps (missing when they were not run)."""
        nan = math.nan
        boot = self.bootstrap
        ci = boot.ci if boot else None
        test = boot.linearity if boot else None
        cont = boot.continuity if boot else None
        return {
            "gamma_lo": ci.lo if ci else nan,
            "gamma_hi": ci.hi if ci else nan,
            "ci_empty": ci.empty if ci else nan,
            "ci_nseg": ci.n_segments if ci else nan,
            "ci_incomplete": ci.incomplete if ci else nan,
            "ci_unresolved": float(ci.n_unresolved) if ci else nan,
            "boundary_warn": float(ci.boundary_warn) if ci else 0.0,
            "pval_lin": test.p_value if test else nan,
            "boot_linearity_valid": float(test.n_valid) if test else nan,
            "rseed": float(boot.seed) if boot and boot.seed is not None else nan,
            "pval_cont": cont.p_value if cont else nan,
            "boot_continuity_valid": float(cont.n_valid) if cont else nan,
            **self._citest_scalars(),
            **self._coefficient_scalars(),
        }

    def _coefficient_scalars(self) -> dict[str, float]:
        """Bookkeeping of the coefficient bootstrap (absent unless it was requested)."""
        coef = self.bootstrap.coefficient if self.bootstrap else None
        if coef is None:
            return {}
        return {
            "boot_coef_B": float(coef.n_valid),
            "boot_coef_attempted": float(coef.n_attempted),
            "boot_coef_failed": float(coef.n_failed),
            "boot_coef_twostep": float(coef.n_twostep),
            "boot_grid_stage1": float(coef.n_stage1),
            "boot_grid_stage2": float(coef.n_stage2),
        }

    def _citest_scalars(self) -> dict[str, float]:
        """Scalars of ``citest`` (absent unless it was requested)."""
        check = self.bootstrap.citest if self.bootstrap else None
        if check is None:
            return {}
        return {
            "citest_gamma": check.gamma, "citest_D": check.statistic,
            "citest_crit": check.crit, "citest_accept": check.accepted,
            "citest_draws": check.n_valid, "citest_status": check.status,
            "citest_p": check.p_value,
        }  # fmt: skip

    def predict(
        self,
        kind: str,
        frame: pd.DataFrame,
        *,
        where: str | Sequence[bool] | BoolArray | None = None,
    ) -> pd.Series:
        """Return ``"residuals"``, ``"xb"``, ``"ar_residuals"`` or ``"regime"`` for ``frame``.

        ``frame`` is the data the model was estimated on; the result is aligned with it and
        missing where the series is not defined.  ``where`` restricts the rows (Stata ``if``).
        """
        fit = self.search.fit
        return predict_series(
            kind, frame, data=self.data, stack=self.stack, test_stack=self.serial.stack,
            gamma=fit.gamma, theta=fit.theta, q=self.spec.q, id=self.id, time=self.time,
            where=where,
        )  # fmt: skip

    @property
    def upper(self) -> UpperRegime | None:
        """Slopes of the upper regime and their variance (``e(b_upper)``, ``e(V_upper)``)."""
        theta = self.search.fit.theta
        return upper_regime(
            theta, self.variance.cov, self.names, kink=self.stack.kink, q=self.spec.q
        )


def _warn(key: str, **fields: Any) -> None:
    warnings.warn(message(key, **fields), PyxdpthreshWarning, stacklevel=3)


def _warn_variance(vce: str, twostep: bool, variance: VarianceFit) -> None:
    """Warn about the variance that was delivered."""
    # Stata: notes after the table (xtdpthresh.ado:1868-1893)
    if vce == "windmeijer" and not variance.wind_applied:
        _warn("warn_wind_not_applied")
    if variance.wind_applied and variance.same_threshold == 0:
        _warn("warn_wind_same_threshold")
    if not variance.joint:
        _warn("warn_joint_unavailable")
    elif not math.isnan(variance.q_nvals_bw) and variance.q_nvals_bw < MIN_Q_VALUES:
        _warn("warn_q_few_values", n=int(variance.q_nvals_bw))


def projected_columns(data: XtdpthreshData) -> int:
    """Instrument columns the per-period layout would have before any column is removed."""
    # Stata: xtdpthresh_run, "about N instrument columns" (xtdpthresh.ado:8615-8639)
    opts = data.spec.options
    n_periods = int(observed_periods(data.time, data.eq).size)
    span = int(np.max(data.time) - np.min(data.time)) if data.time.size else 0
    hi = span if opts.maxlag[1] >= span else int(opts.maxlag[1])
    lag_y = max(hi - max(opts.maxlag[0], 2) + 1, 0)
    lag_p = max(hi - max(opts.maxlag[0], 1) + 1, 0)
    kinds = data.var_type
    k_endog, k_predet, k_exog = (int(np.sum(kinds == k)) for k in (3, 4, 2))
    per_period = 1 + (0 if opts.static else lag_y) + k_endog * lag_y + k_predet * lag_p + k_exog
    k_iv = len(data.spec.iv)
    external = (k_iv if opts.iv_collapse else n_periods * k_iv) if k_iv else 0
    return n_periods * per_period + external


def _warn_instruments(data: XtdpthreshData) -> None:
    if data.spec.options.collapse:
        return
    cols = projected_columns(data)
    if cols > WARN_COLUMNS:
        _warn("warn_iv_wide", cols=cols)
    elif cols > NOTE_COLUMNS:
        _warn("warn_iv_many", cols=cols)


def _fit_point(
    frame: pd.DataFrame,
    y: str,
    x: Sequence[str] | str = (),
    *,
    q: str,
    id: str | None = None,
    time: str | None = None,
    where: str | Sequence[bool] | BoolArray | None = None,
    grid_values: FloatArray | None = None,
    **options: Any,
) -> PointFit:
    """Estimate and run the inference; the body of :func:`fit_point`."""
    # Stata: xtdpthresh_run (xtdpthresh.ado:8461) for the point estimate
    spec = check_specification(y=y, x=x, q=q, **options)
    data = prepare_data(frame, spec, id=id, time=time, where=where)
    opts = spec.options
    if opts.warn:
        _warn_instruments(data)
    stack = build_stack(data)
    result = search_threshold(
        stack,
        grid=opts.grid,
        grid_type=opts.grid_type,
        observed_support=opts.grid_sample == "observed",
        trim=opts.trim,
        min_regime=opts.min_regime,
        refine=opts.refine,
        center=opts.center,
        grid_values=grid_values,
    )
    if opts.warn and opts.refine > 0:
        if not result.fit.twostep:
            _warn("warn_refine_one_step")
        elif result.refine is None or not result.refine.complete:
            _warn("warn_refine_incomplete")
    support, _ = threshold_support(stack, opts.grid_sample == "observed")
    fit = result.fit
    variance = final_variance(
        stack, fit, result.stage1_gamma, vce=opts.vce, bw_scale=opts.bw_scale,
        center=opts.center, support=support,
    )  # fmt: skip
    if opts.warn:
        _warn_variance(opts.vce, fit.twostep, variance)
    hansen = hansen_test(fit.obj, stack.n_instruments, fit.theta.size, twostep=fit.twostep)
    serial = serial_tests(data, stack, fit, variance)
    inference = None
    if opts.bootstrap:
        inference = run_bootstrap(
            stack, result, support, trim=opts.trim, grid_ci=opts.grid_ci,
            grid_type=opts.grid_type, n_boot=opts.n_boot, level=opts.level, seed=opts.seed,
            linearity=opts.linearity_test, continuity=opts.continuity_test, citest=opts.gamma_test,
            coef_boot=opts.coef_boot, coef_symmetric=opts.coef_ci_type == "symmetric",
            center=opts.center, boot_type=opts.boot_type,
        )  # fmt: skip
    return PointFit(
        spec,
        data,
        stack,
        result,
        variance,
        hansen,
        serial,
        stack.n_switch(fit.gamma),
        id,
        time,
        inference,
    )


def fit_point(
    frame: pd.DataFrame,
    y: str,
    x: Sequence[str] | str = (),
    *,
    q: str,
    id: str | None = None,
    time: str | None = None,
    where: str | Sequence[bool] | BoolArray | None = None,
    grid_values: FloatArray | None = None,
    **options: Any,
) -> PointFit:
    """Estimate the dynamic panel threshold model in first differences (point estimates).

    Parameters
    ----------
    frame
        Long data, one row per (unit, period).
    y, x, q
        Dependent variable, regressors and threshold variable.
    id, time
        Identifier and time columns (or index level names).
    where
        Condition selecting the equation sample.
    grid_values
        Explicit candidate thresholds, instead of the grid built from ``grid``.
    **options
        Any argument of :func:`check_specification` (``endogenous``, ``maxlag``, ``collapse``,
        ``kink``, ``grid``, ``refine``...).
    """
    with blas_threads():
        return _fit_point(
            frame, y, x, q=q, id=id, time=time, where=where, grid_values=grid_values, **options
        )
