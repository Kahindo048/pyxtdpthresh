"""Variance of the slope estimates: conditional, joint with the threshold, and Windmeijer.

Three layers, as in the Stata command:

* the **conditional** variance treats the threshold as known: the cluster-robust sandwich of the
  weight that was used (``ThresholdFit.cov``);
* the **Windmeijer** correction (``vce="windmeijer"``) adds the first-step estimation error of the
  second-step weight to that sandwich;
* the **joint** variance (always attempted) adds the threshold as one more parameter.  The sample
  moments are step functions of ``gamma`` in the jump model, but their expectation is smooth, so
  the derivative column is a kernel ``x_g = -T(phi_h(q - gamma) (1, x') delta)`` with bandwidth
  ``h = bwscale * 1.06 * s_q * n^(-1/5)`` (Seo-Shin 2016, as in ``xthenreg``).  In the kink model
  the moment is continuous and the derivative is analytic, ``x_g = -delta_k T(1(q > gamma))``.
  The slope variance is the ``theta`` block of the sandwich of the design augmented by ``x_g``.

The joint variance is the one reported; the conditional one is kept as ``e(V_cond)``.  When the
corrected variance is not positive semidefinite both corrections are dropped and the cluster-robust
variances are reported, so ``e(V)``, ``e(V_cond)`` and the serial-correlation tests stay consistent.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from pyxtdpthresh._types import FloatArray
from pyxtdpthresh.core.gmm import sandwich
from pyxtdpthresh.core.linalg import psd_ok, syminv
from pyxtdpthresh.models.xtdpthresh.estimator import (
    ThresholdFit,
    moments_by_unit,
    omega_of,
    problem_at,
)
from pyxtdpthresh.models.xtdpthresh.stack import Stack

#: Distinct values of ``q`` within two bandwidths below which the kernel derivative is doubtful.
MIN_Q_VALUES = 10


@dataclass(frozen=True)
class VarianceFit:
    """Reported variance of the slopes and what produced it.

    Attributes
    ----------
    cov
        Variance of ``theta`` that is reported (``e(V)``): joint with the threshold when
        ``joint``, conditional on it otherwise.
    cond
        Conditional variance of the same type (Windmeijer when applied, else robust): ``e(V_cond)``.
    robust
        Cluster-robust conditional variance of the weight that was used.
    joint
        The joint variance could be computed (``e(joint_vce)``).
    wind_applied
        The Windmeijer correction replaced the robust variance (``e(vce_applied)``).
    same_threshold
        Whether ``W2`` was built at the reported design (``e(wind_same_threshold)``); missing
        under the joint variance, which differentiates ``W2`` in the first-step threshold too.
    bandwidth
        Kernel bandwidth (``e(gamma_bw)``); missing for the kink model or without a joint variance.
    q_nvals_bw
        Distinct values of ``q`` within two bandwidths of the threshold (``e(q_nvals_bw)``).
    full
        Joint variance of ``(theta, gamma)`` (``None`` without a joint variance).
    """

    cov: FloatArray
    cond: FloatArray
    robust: FloatArray
    joint: bool
    wind_applied: bool
    same_threshold: float
    bandwidth: float
    q_nvals_bw: float
    full: FloatArray | None


def _augment(zw: FloatArray, stack: Stack, derivative: FloatArray) -> FloatArray:
    """``[Z'X/n, Z'x_g/n]``: the Jacobian with the threshold as one more parameter."""
    column = stack.z.rmatmul(derivative[:, None]) / stack.n_rows
    return np.column_stack([zw, column])


def windmeijer(
    stack: Stack,
    *,
    zw1: FloatArray,
    x1: FloatArray,
    zw2: FloatArray,
    w1: FloatArray,
    w2: FloatArray,
    omega1: FloatArray,
    resid1: FloatArray,
    gbar2: FloatArray,
    center: bool,
) -> FloatArray | None:
    """Windmeijer (2005) variance of the two-step estimator with ``W2`` fixed.

    ``W2 = Omega(theta_1)^{-1}`` depends on the first-step estimate.  Linearising the second-step
    estimate in ``theta_1`` adds the term ``D_j = -B2 G'W2 [dOmega/dtheta_j] W2 gbar2`` with
    ``B2 = (G'W2 G)^{-1}``, and the variance of the linearised estimator is ``M Omega_1 M' / n``
    with ``M = B2 G'W2 + D B1 G1'W1``.  The derivative of ``Omega`` is never formed: only its
    product with ``W2 gbar2`` is needed, which costs two products per column instead of a
    ``L x L`` matrix.

    Parameters
    ----------
    stack
        System (instruments and unit structure).
    zw1, x1, w1
        ``Z'X/n``, transformed regressors and weight of the first step.
    zw2, w2, gbar2
        ``Z'X/n``, weight and moment residuals ``Z'(y - X theta)/n`` of the second step.
    omega1, resid1
        Moment covariance and residuals of the first step (they built ``W2``).
    center
        Whether ``Omega`` was centred.

    Returns
    -------
    numpy.ndarray or None
        The variance, or ``None`` when a bread cannot be inverted or the result is not finite.
    """
    # Stata: xdpt2_windmeijer (xtdpthresh.ado:4889)
    k = zw2.shape[1]
    if x1.shape[1] != k or zw1.shape[1] != k:
        return None
    n, clusters = stack.n_rows, stack.n_units
    second = syminv(zw2.T @ w2 @ zw2)
    first = syminv(zw1.T @ w1 @ zw1)
    if not (second.ok and first.ok):
        return None
    gm = moments_by_unit(stack, resid1)
    v = w2 @ gbar2
    gv = gm @ v
    gsum = gm.sum(axis=0)
    left = zw2.T @ w2
    derivative = np.empty((k, k))
    for j in range(k):
        hj = moments_by_unit(stack, x1[:, j])
        # dOmega/dtheta_j v = -(H'G + G'H) v / n, plus the centring term of Omega
        dv = -(hj.T @ gv + gm.T @ (hj @ v)) / n
        if center:
            hsum = hj.sum(axis=0)
            dv = dv + (hsum * (gsum @ v) + gsum * (hsum @ v)) / (clusters * n)
        derivative[:, j] = -second.inv @ (left @ dv)
    m = second.inv @ left + derivative @ (first.inv @ (zw1.T @ w1))
    cov = m @ omega1 @ m.T / n
    cov = (cov + cov.T) / 2
    return cov if bool(np.all(np.isfinite(cov))) else None


def _kernel_derivative(
    stack: Stack, gamma: float, theta: FloatArray, bandwidth: float
) -> FloatArray | None:
    """Return the derivative column ``x_g`` of the residuals in the threshold, or ``None``."""
    if not math.isfinite(gamma) or not np.all(np.isfinite(theta)):
        return None
    if not stack.kink and not (math.isfinite(bandwidth) and bandwidth > 0):
        return None
    column = stack.regime_derivative(gamma, theta, bandwidth)
    return column if bool(np.all(np.isfinite(column))) else None


def _same_threshold(stack: Stack, stage1_gamma: float, gamma: float, support: FloatArray) -> float:
    """1 when the first-step threshold gives the reported design (no support point between)."""
    # Stata: same_thr (xtdpthresh.ado:9667)
    if not (math.isfinite(stage1_gamma) and math.isfinite(gamma)):
        return math.nan
    if stack.kink:
        return float(stage1_gamma == gamma)
    low, high = min(stage1_gamma, gamma), max(stage1_gamma, gamma)
    return float(not np.any((support > low) & (support <= high)))


def _count_values(stack: Stack, gamma: float, bandwidth: float) -> float:
    """Distinct values of ``q`` within two bandwidths of ``gamma``."""
    # Stata: xdpt2_q_nvals (xtdpthresh.ado:5121)
    if not (math.isfinite(gamma) and math.isfinite(bandwidth) and bandwidth > 0):
        return math.nan
    close = np.abs(stack.q_values - gamma) <= 2.0 * bandwidth
    return float(np.count_nonzero(close))


def final_variance(
    stack: Stack,
    fit: ThresholdFit,
    stage1_gamma: float,
    *,
    vce: str,
    bw_scale: float,
    center: bool,
    support: FloatArray,
) -> VarianceFit:
    """Variance of the final estimate: robust, Windmeijer-corrected, and joint with the threshold.

    Parameters
    ----------
    stack
        System of the fit.
    fit
        Final estimate (second step unless the estimator stayed at one step).
    stage1_gamma
        Threshold of the first step, where the second-step weight was built.
    vce
        ``"robust"`` or ``"windmeijer"``; the correction exists only for a second-step fit.
    bw_scale
        Multiplier of the kernel bandwidth.
    center
        Centre the moment covariance.
    support
        Values of ``q`` that define the threshold grid (for the ``wind_same_threshold`` flag).
    """
    # Stata: end of xdpt2_grid_search (xtdpthresh.ado:6210-6342, 5859-5891)
    n = stack.n_rows
    step = problem_at(stack, fit.gamma)
    omega = omega_of(stack, step.residual(stack, fit.theta), center=center)
    robust = fit.cov
    reported, applied = robust, False

    if vce == "windmeijer" and fit.twostep:
        step_1 = problem_at(stack, stage1_gamma)
        resid_1 = step_1.residual(stack, fit.first_theta)
        omega_1 = omega_of(stack, resid_1, center=center)
        gbar = stack.zy - step.zw @ fit.theta
        corrected = windmeijer(
            stack, zw1=step_1.zw, x1=step_1.regressors, zw2=step.zw,
            w1=stack.first_weight.weight, w2=fit.weight, omega1=omega_1,
            resid1=resid_1, gbar2=gbar, center=center,
        )  # fmt: skip
        if corrected is not None and psd_ok(corrected):
            reported, applied = corrected, True

    bandwidth = math.nan if stack.kink else stack.bandwidth(bw_scale)
    full: FloatArray | None = None
    g2 = _kernel_derivative(stack, fit.gamma, fit.theta, bandwidth)
    if g2 is not None:
        if applied:
            g1 = _kernel_derivative(stack, stage1_gamma, fit.first_theta, bandwidth)
            if g1 is not None:
                full = windmeijer(
                    stack,
                    zw1=_augment(step_1.zw, stack, g1),
                    x1=np.column_stack([step_1.regressors, g1]),
                    zw2=_augment(step.zw, stack, g2),
                    w1=stack.first_weight.weight, w2=fit.weight, omega1=omega_1,
                    resid1=resid_1, gbar2=gbar, center=center,
                )  # fmt: skip
                if full is not None and not psd_ok(full):
                    # both corrections are dropped: the robust variances stay consistent
                    reported, applied = robust, False
                    full = sandwich(_augment(step.zw, stack, g2), fit.weight, omega, n)
        else:
            full = sandwich(_augment(step.zw, stack, g2), fit.weight, omega, n)

    k = step.zw.shape[1]
    joint = full is not None and bool(np.all(np.isfinite(full[:k, :k])))
    cov = full[:k, :k] if joint and full is not None else reported
    same = math.nan if joint else _same_threshold(stack, stage1_gamma, fit.gamma, support)
    count = math.nan if (stack.kink or not joint) else _count_values(stack, fit.gamma, bandwidth)
    return VarianceFit(
        cov=cov,
        cond=reported,
        robust=robust,
        joint=joint,
        wind_applied=applied,
        same_threshold=same if applied else math.nan,
        bandwidth=bandwidth if (joint and not stack.kink) else math.nan,
        q_nvals_bw=count,
        full=full if joint else None,
    )
