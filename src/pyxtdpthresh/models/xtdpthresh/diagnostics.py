"""Specification tests: Hansen over-identification and Arellano-Bond serial correlation.

* **Hansen J** is the criterion of the second-step estimator, ``chi2`` with ``L - k - 1`` degrees of
  freedom (the threshold is a parameter too).  A one-step fit has no efficient weight and reports
  no statistic.
* **AR(k)** is the Arellano-Bond (1991, eq. 8) statistic ``m_k = b0 / sqrt(T1 + T2 + T3)`` on the
  first-difference residuals, whatever the estimation transformation (the ``xtabond2``
  convention).  ``b0`` is the sum over units of the products of residuals ``k`` periods apart,
  ``T1`` the sum of squared unit sums, ``T2`` the covariance with the estimation error of
  ``theta`` and ``T3`` the direct contribution of its variance.  With the joint variance the
  threshold is a parameter of ``T2`` and ``T3`` too.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, replace
from typing import NamedTuple

import numpy as np
from scipy.special import gammaincc, ndtr

from pyxtdpthresh._types import FloatArray, IntArray
from pyxtdpthresh.core.linalg import syminv
from pyxtdpthresh.instruments.matrix import InstrumentMatrix
from pyxtdpthresh.models.xtdpthresh.estimator import ThresholdFit
from pyxtdpthresh.models.xtdpthresh.sample import XtdpthreshData
from pyxtdpthresh.models.xtdpthresh.stack import Stack, build_stack
from pyxtdpthresh.models.xtdpthresh.variance import VarianceFit

#: Fewest residual pairs, and units contributing them, for which the statistic is computed.
MIN_PAIRS = 5


class HansenTest(NamedTuple):
    """Hansen J statistic, degrees of freedom and p-value (``nan`` when not defined)."""

    statistic: float
    df: float
    p_value: float


def hansen_test(obj: float, n_instruments: int, n_parameters: int, *, twostep: bool) -> HansenTest:
    """Hansen J of the second-step criterion.

    ``n_parameters`` counts the coefficients; the threshold adds one.  Nothing is reported for a
    one-step fit or when the model is not over-identified.
    """
    # Stata: xdpt2_hansen_j (xtdpthresh.ado:8048)
    df = n_instruments - n_parameters - 1
    if not twostep or df <= 0:
        return HansenTest(math.nan, math.nan, math.nan)
    return HansenTest(obj, float(df), float(gammaincc(df / 2.0, obj / 2.0)))


class ARTest(NamedTuple):
    """One Arellano-Bond statistic.

    Attributes
    ----------
    statistic, p_value
        ``m_k`` and its two-sided normal p-value.
    n_pairs
        Residual pairs used; negative when the estimation-error terms could not be formed.
    b0, t1, tt
        The numerator ``b0``, the term ``T1`` and the sum ``T2 + T3``.
    n_clusters
        Units contributing at least one pair.
    """

    statistic: float
    n_pairs: float
    p_value: float
    b0: float
    t1: float
    tt: float
    n_clusters: float


_NONE = ARTest(*(math.nan,) * 6, 0.0)


@dataclass(frozen=True)
class ARSample:
    """Residual system on which a serial-correlation test is run (first differences).

    Attributes
    ----------
    resid, regressors
        Residuals and regressors of the transformed equations ``(n,)`` and ``(n, p)``.
    unit, time
        Unit index and period of each row, sorted by unit and period.
    """

    resid: FloatArray
    regressors: FloatArray
    unit: IntArray
    time: IntArray


@dataclass(frozen=True)
class EstimationRows:
    """Estimation system that links the test to the estimate.

    Attributes
    ----------
    resid, regressors
        Residuals ``(n,)`` and regressors ``(n, p)`` of the estimation equations.
    z
        Instrument matrix.
    unit
        Unit index of each estimation row.
    weight
        Weight matrix paired with the estimate.
    n_units
        Number of units of the data (length of the per-unit vectors).
    """

    resid: FloatArray
    regressors: FloatArray
    z: InstrumentMatrix
    unit: IntArray
    weight: FloatArray
    n_units: int


def _lag_partners(unit: IntArray, time: IntArray, order: int) -> IntArray:
    """Row of the same unit ``order`` periods earlier, or -1 (rows sorted by unit and period)."""
    if time.size == 0:
        return np.empty(0, dtype=np.int64)
    low = int(np.min(time))
    span = int(np.max(time)) - low + order + 1
    key = unit.astype(np.int64) * span + (time - low + order)
    want = key - order
    at = np.searchsorted(key, want)
    at = np.minimum(at, key.size - 1)
    found = key[at] == want
    return np.where(found, at, -1).astype(np.int64)


def ar_test(order: int, test: ARSample, est: EstimationRows, cov: FloatArray) -> ARTest:
    """Arellano-Bond ``m_order`` statistic with the estimation-error terms.

    Parameters
    ----------
    order
        Lag ``k`` of the autocorrelation tested.
    test
        First-difference residual system.
    est
        Estimation system, its weight and instruments.
    cov
        Variance of the parameters (``(p, p)``); conditional or joint with the threshold.
    """
    # Stata: xdpt2_ar_full (xtdpthresh.ado:8092)
    n = test.resid.size
    if n < 2:
        return _NONE
    partner = _lag_partners(test.unit, test.time, order)
    found = partner >= 0
    lagged = np.where(found, test.resid[np.maximum(partner, 0)], 0.0)
    cross = test.resid * lagged
    unit_sum = np.bincount(test.unit, weights=cross, minlength=est.n_units)
    pairs_by_unit = np.bincount(test.unit[found], minlength=est.n_units)
    n_pairs = int(found.sum())
    n_clusters = int(np.count_nonzero(pairs_by_unit))
    b0 = float(unit_sum.sum())
    t1 = float(np.sum(unit_sum**2))
    if t1 <= 0 or n_pairs < MIN_PAIRS or n_clusters < MIN_PAIRS:
        return ARTest(math.nan, math.nan, math.nan, b0, t1, math.nan, float(n_clusters))

    p = cov.shape[0]
    shapes = (
        test.regressors.shape[0] == n
        and est.resid.size > 0
        and est.z.shape[0] == est.resid.size == est.regressors.shape[0]
        and est.weight.shape == (est.z.shape[1],) * 2
        and p == est.regressors.shape[1]
        and test.regressors.shape[1] <= p
    )
    tt = math.nan
    if shapes:
        g = np.zeros(p)
        g[: test.regressors.shape[1]] = test.regressors.T @ lagged
        s = est.z.rmatmul((est.resid * unit_sum[est.unit])[:, None])[:, 0]
        moments = est.z.rmatmul(est.regressors).T  # raw sums, (p, L)
        gag = syminv(moments @ est.weight @ moments.T)
        if gag.ok:
            t2 = -2.0 * float(g @ (gag.inv @ (moments @ (est.weight @ s))))
            t3 = float(g @ cov @ g)
            tt = t2 + t3
    if not math.isfinite(tt):
        return ARTest(math.nan, -float(n_pairs), math.nan, b0, t1, math.nan, float(n_clusters))
    denominator = t1 + tt
    if not denominator > 0:
        return ARTest(math.nan, -float(n_pairs), math.nan, b0, t1, tt, float(n_clusters))
    statistic = b0 / math.sqrt(denominator)
    return ARTest(
        statistic, float(n_pairs), float(2.0 * ndtr(-abs(statistic))), b0, t1, tt, float(n_clusters)
    )


@dataclass(frozen=True)
class SerialTests:
    """AR(1) and AR(2) tests of a fit.

    Attributes
    ----------
    ar1, ar2
        Reported statistics: with the threshold as a parameter when ``joint``, else conditional.
    ar1_cond, ar2_cond
        Statistics that treat the threshold as known (``xtabond2`` at fixed ``gamma``).
    joint
        The reported statistics include the estimation of the threshold (``e(ar_joint)``).
    stack
        First-difference system on which the tests are run (the estimation stack under FD).
    """

    ar1: ARTest
    ar2: ARTest
    ar1_cond: ARTest
    ar2_cond: ARTest
    joint: bool
    stack: Stack


def first_difference_stack(data: XtdpthreshData, stack: Stack) -> Stack:
    """Return the first-difference system of the data (the estimation stack under ``fd``)."""
    # Stata: AR tests always on first-difference residuals (xtdpthresh.ado:9370)
    if data.spec.options.method == "fd":
        return stack
    options = replace(data.spec.options, method="fd")
    return build_stack(replace(data, spec=replace(data.spec, options=options)))


def serial_tests(
    data: XtdpthreshData, stack: Stack, fit: ThresholdFit, variance: VarianceFit
) -> SerialTests:
    """AR(1) and AR(2) of the final estimate, conditional and (when available) joint."""
    # Stata: AR block of xtdpthresh_run (xtdpthresh.ado:9370-9469)
    test_stack = first_difference_stack(data, stack)
    gamma, theta = fit.gamma, fit.theta
    x_est = stack.regressors(gamma)
    x_test = x_est if test_stack is stack else test_stack.regressors(gamma)
    est = EstimationRows(
        stack.dy - x_est @ theta, x_est, stack.z, stack.unit, fit.weight, data.n_units
    )
    rows = ARSample(test_stack.dy - x_test @ theta, x_test, test_stack.unit, test_stack.time)
    cond = [ar_test(k, rows, est, variance.cond) for k in (1, 2)]
    reported, joint = cond, False
    if variance.full is not None:
        bandwidth = variance.bandwidth
        g_est = stack.regime_derivative(gamma, theta, bandwidth)
        g_test = (
            g_est if test_stack is stack else test_stack.regime_derivative(gamma, theta, bandwidth)
        )
        if np.all(np.isfinite(g_est)) and np.all(np.isfinite(g_test)):
            est_j = replace(est, regressors=np.column_stack([x_est, g_est]))
            rows_j = replace(rows, regressors=np.column_stack([x_test, g_test]))
            both = [ar_test(k, rows_j, est_j, variance.full) for k in (1, 2)]
            lost = any(
                math.isnan(j.statistic) and not math.isnan(c.statistic)
                for j, c in zip(both, cond, strict=True)
            )
            if not lost:
                reported, joint = both, True
    return SerialTests(reported[0], reported[1], cond[0], cond[1], joint, test_stack)
