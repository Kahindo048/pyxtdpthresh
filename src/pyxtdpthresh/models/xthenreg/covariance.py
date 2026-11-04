"""Asymptotic covariance matrix and confidence intervals of ``xthenreg``.

Seo and Shin (2016, p. 173): with ``G = (G_b, G_d, G_r)`` the derivatives of the moments with
respect to the linear coefficients, the regime coefficients and the threshold, and ``Omega^-1``
the second-step weight, the covariance of ``(theta, gamma)`` is ``(G' Omega^-1 G)^-1 / N``.
With a jump the derivative with respect to the threshold needs a kernel (Gaussian, bandwidth
``h = h_0 * 1.06 * N^-0.2 * sd(q)``); with a kink it is available in closed form.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.stats import norm

from pyxtdpthresh._types import FloatArray
from pyxtdpthresh.core.linalg import cholinv
from pyxtdpthresh.models.xthenreg.estimator import TwoStepFit
from pyxtdpthresh.models.xthenreg.moments import XthenregProblem

#: 0.975 quantile of the standard normal, as typed in the Stata code.
Z_975 = 1.959963984540054
#: Default multiplier of the kernel bandwidth.
H_0 = 1.5


@dataclass(frozen=True)
class CovarianceResult:
    """Covariance, standard errors and 95 % confidence intervals.

    Attributes
    ----------
    cov
        Covariance of the coefficients and the threshold.
    se
        Standard errors (NaN where the variance is not positive).
    ci
        ``(p, 2)`` lower and upper limits of the 95 % interval.
    bandwidth
        Kernel bandwidth (NaN for a kink, which does not use one).
    jacobian
        The matrix ``G = (G_b, G_d, G_r)``.
    """

    cov: FloatArray
    se: FloatArray
    ci: FloatArray
    bandwidth: float
    jacobian: FloatArray


def bandwidth(problem: XthenregProblem, h_0: float = H_0) -> float:
    """Kernel bandwidth ``h_0 * 1.06 * N^(-0.2) * sd(q)`` (``sd`` over all N * T values)."""
    return float(h_0 * 1.06 * problem.n_units ** (-0.2) * np.sqrt(np.var(problem.level_q, ddof=1)))


def _pair_sums(problem: XthenregProblem, per_level: FloatArray) -> FloatArray:
    """Sum the weighted level terms of each equation row (``t`` minus ``t - 1``)."""
    weighted = per_level[problem.pair_lev] * (
        problem.pair_w if per_level.ndim == 1 else problem.pair_w[:, None]
    )
    return np.asarray(np.add.reduceat(weighted, problem.pair_ptr[:-1], axis=0), dtype=np.float64)


def _jump_threshold_derivative(
    problem: XthenregProblem, fit: TwoStepFit, band: float
) -> FloatArray:
    """``G_r`` for a jump: the kernel-smoothed derivative of the moments in the threshold."""
    k = problem.k
    gamma = fit.second.gamma
    delta = fit.second.theta[k:]  # (delta_0, delta)
    density = norm.pdf((gamma - problem.level_q) / band)
    per_level = (problem.regime_levels @ delta) * density
    z = problem.inst.z
    # temp_z = [1, x_{t-1}] delta phi_{t-1} - [1, x_t] delta phi_t = - sum_pairs w (...)
    return np.asarray(z.T @ (-_pair_sums(problem, per_level))) / (problem.n_units * band)


def covariance(problem: XthenregProblem, fit: TwoStepFit, h_0: float = H_0) -> CovarianceResult:
    """Covariance matrix, standard errors and 95 % intervals of the step-2 estimates.

    Parameters
    ----------
    problem, fit
        The data and the two-step fit.
    h_0
        Multiplier of the kernel bandwidth (jump models only).
    """
    # Stata: cov_mat_con (xthenreg.ado:1532) and cov_mat_con_kink (1594)
    # STATA-QUIRK: with a kink G_d has the positive sign (unlike the jump model) and G_r uses the
    # indicator of the regime above the threshold, as in cov_mat_con_kink.
    k = problem.k
    n = problem.n_units
    a_hat = fit.a[fit.second.index]  # A(gamma_hat), (L, n_params)
    g_b = -problem.zdx
    if problem.kink:
        band = float("nan")
        g_d = a_hat[:, k:]
        kappa = fit.second.theta[k]
        indicator = _pair_sums(problem, (problem.level_q > fit.second.gamma).astype(float))
        g_r = -kappa * np.asarray(problem.inst.z.T @ indicator) / n
    else:
        band = bandwidth(problem, h_0)
        g_d = -a_hat[:, k:]
        g_r = _jump_threshold_derivative(problem, fit, band)
    jacobian = np.column_stack([g_b, g_d, g_r])
    cov = cholinv(jacobian.T @ fit.omega_inv @ jacobian) / n
    with np.errstate(invalid="ignore"):
        se = np.sqrt(np.diag(cov))
    estimates = fit.estimates
    ci = np.column_stack([estimates - Z_975 * se, estimates + Z_975 * se])
    return CovarianceResult(cov, se, ci, band, jacobian)
