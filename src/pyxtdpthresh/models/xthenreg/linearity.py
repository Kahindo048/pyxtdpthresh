"""Linearity test of ``xthenreg``: sup-Wald statistic and fast wild bootstrap.

H0: the regime coefficients are zero (no threshold effect).  The Wald statistic of the regime
coefficients is computed at every grid point, each time with its own two-step estimate and
covariance, and the test statistic is the supremum over the grid.  The p-value comes from the
fast bootstrap of Seo, Kim and Kim (2019): the step-2 moments of each unit are multiplied by a
standard normal weight, the one-step estimator is re-evaluated with the *fixed* step-2 weight at
every grid point, and the Wald form reuses the covariance matrices of the original sample.

Quirk of the Stata command, reproduced: with a kink, the tested block has two entries (the last
linear coefficient and the kink coefficient, ``dlt_len = 2``) instead of the kink coefficient alone.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from pyxtdpthresh._types import FloatArray
from pyxtdpthresh.core.gmm import solve_grid
from pyxtdpthresh.core.linalg import cholinv
from pyxtdpthresh.core.weights import second_step_weight
from pyxtdpthresh.models.xthenreg.estimator import TwoStepFit
from pyxtdpthresh.models.xthenreg.moments import (
    XthenregProblem,
    moments_by_unit,
    residual_rows,
)


@dataclass(frozen=True)
class SupWald:
    """Wald statistics of the sample at every grid point.

    Attributes
    ----------
    wald
        Statistic at each grid point, ``(G,)``.
    sup
        Supremum over the grid (missing values ignored).
    cov_wald
        Covariance of the tested coefficients at each grid point, ``(G, d, d)``.
    length
        Number of tested coefficients ``d`` (``dlt_len`` of the Stata code).
    """

    wald: FloatArray
    sup: float
    cov_wald: FloatArray
    length: int


@dataclass(frozen=True)
class LinearityTest:
    """Result of the bootstrap linearity test.

    Attributes
    ----------
    p_value
        Share of bootstrap suprema above the sample supremum.
    sup_wald
        Sample statistic.
    boot_sup
        Supremum of each bootstrap replication, ``(B,)``.
    """

    p_value: float
    sup_wald: float
    boot_sup: FloatArray


def tested_length(problem: XthenregProblem) -> int:
    """Number of coefficients tested: all regime coefficients, or 2 with a kink (a quirk)."""
    # Stata: sup_wald_cal (xthenreg.ado:1697-1714)
    return 2 if problem.kink else problem.k + 1


def sup_wald(problem: XthenregProblem, fit: TwoStepFit) -> SupWald:
    """Sup-Wald statistic of the sample, with a full two-step estimate at each grid point."""
    # Stata: sup_wald_cal (xthenreg.ado:1683)
    k, n, d = problem.k, problem.n_units, tested_length(problem)
    n_grid = fit.grid.size
    wald = np.full(n_grid, np.nan)
    cov_wald = np.full((n_grid, d, d), np.nan)
    sign = 1.0 if problem.kink else -1.0
    for g, gamma in enumerate(fit.grid):
        a_g = fit.a[g : g + 1]
        resid1 = residual_rows(problem, fit.first.solution.theta[g], float(gamma))
        weight2 = second_step_weight(moments_by_unit(problem, resid1))
        theta2 = solve_grid(a_g, problem.zy, weight2).theta[0]
        resid2 = residual_rows(problem, theta2, float(gamma))
        omega = second_step_weight(moments_by_unit(problem, resid2))
        jac = np.column_stack([-problem.zdx, sign * fit.a[g][:, k:]])
        try:
            chol = np.linalg.cholesky(omega)
        except np.linalg.LinAlgError:
            continue  # Mata: cholesky() of a matrix that is not positive definite is missing
        v_s = chol.T @ jac
        cov = cholinv(v_s.T @ v_s)[-d:, -d:]
        delta = theta2[-d:]
        cov_wald[g] = cov
        wald[g] = n * delta @ cholinv(cov) @ delta
    sup = float(np.nanmax(wald)) if np.any(~np.isnan(wald)) else float("nan")
    return SupWald(wald, sup, cov_wald, d)


def bootstrap_sup(
    problem: XthenregProblem,
    fit: TwoStepFit,
    sample: SupWald,
    draws: FloatArray,
    chunk: int = 256,
) -> FloatArray:
    """Supremum of the bootstrap Wald statistic for each row of ``draws``.

    Parameters
    ----------
    draws
        Standard normal weights, ``(B, N)``: row ``b`` multiplies the unit moments in
        replication ``b`` (``invnormal(uniform(1, N))`` in the Stata code).
    chunk
        Number of replications evaluated together (bounds memory).
    """
    # Stata: sup_wald_fb (xthenreg.ado:1920)
    n, d = problem.n_units, sample.length
    draws = np.asarray(draws, dtype=np.float64)
    if draws.ndim != 2 or draws.shape[1] != n:
        raise ValueError(f"draws must have shape (B, {n})")
    unit_g = moments_by_unit(problem, fit.resid)  # (N, L): step-2 residual moments
    weight = fit.second.weight
    bread_inv = fit.second.solution.bread_inv  # invsym(A' W A) at every grid point
    # theta_b = (A'WA)^-1 A'W g1b, for all grid points at once
    projector = np.einsum("gpq,glq->gpl", bread_inv, np.matmul(weight, fit.a))  # (G, p, L)
    cov_inv = np.stack([cholinv(c) for c in sample.cov_wald])  # (G, d, d)
    sup = np.empty(draws.shape[0])
    for start in range(0, draws.shape[0], chunk):
        block = draws[start : start + chunk]
        g1 = block @ unit_g / n  # (b, L)
        delta = np.einsum("gpl,bl->bgp", projector, g1)[:, :, -d:]
        wald = n * np.einsum("bgi,gij,bgj->bg", delta, cov_inv, delta)
        all_missing = np.all(np.isnan(wald), axis=1)
        wald[all_missing] = 0.0
        sup[start : start + chunk] = np.where(all_missing, np.nan, np.nanmax(wald, axis=1))
    return sup


def linearity_test(
    problem: XthenregProblem, fit: TwoStepFit, draws: FloatArray, sample: SupWald | None = None
) -> LinearityTest:
    """Bootstrap p-value of the linearity test.

    A bootstrap statistic that is missing counts as exceeding the sample statistic, as a
    missing value does in Mata.
    """
    # Stata: maincode_0719, step 4 (xthenreg.ado:794-831)
    sample = sup_wald(problem, fit) if sample is None else sample
    boot = bootstrap_sup(problem, fit, sample, draws)
    exceed = np.isnan(boot) | (boot > sample.sup)
    return LinearityTest(float(np.mean(exceed)), sample.sup, boot)
