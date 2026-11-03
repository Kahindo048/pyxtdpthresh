"""Generalised method of moments on a grid of thresholds.

At each candidate threshold the linear GMM estimator is

    theta = invsym(A' W A) A' W y,    gbar = y - A theta,    J = gbar' W gbar

with ``A = Z'X(gamma) / n`` the moment-by-parameter matrix and ``y = Z'dy / n`` (Mata:
``GMM_cal`` of ``xthenreg``).  Everything is evaluated for all grid points with batched
matrix products (BLAS) and one batched ``invsym``: this step is dominated by dense algebra,
where a hand-written Numba loop does not beat the library, so it is plain NumPy.
"""

from __future__ import annotations

from typing import NamedTuple

import numpy as np

from pyxtdpthresh._types import FloatArray
from pyxtdpthresh.core.linalg import invsym_batch, syminv


class GridSolution(NamedTuple):
    """GMM solution at every grid point.

    Attributes
    ----------
    theta
        Estimates, ``(G, p)``.
    gbar
        Moment residuals ``y - A theta``, ``(G, L)``.
    crit
        Criterion ``gbar' W gbar``, ``(G,)``.
    bread_inv
        ``invsym(A' W A)``, ``(G, p, p)`` (needed by the variance).
    """

    theta: FloatArray
    gbar: FloatArray
    crit: FloatArray
    bread_inv: FloatArray


def solve_grid(a: FloatArray, y: FloatArray, weight: FloatArray) -> GridSolution:
    """Linear GMM at every grid point for a given weight matrix.

    Parameters
    ----------
    a
        Moment-by-parameter matrices ``(G, L, p)``, one per grid point.
    y
        Moments of the dependent variable ``(L,)``.
    weight
        Weight matrix ``(L, L)`` shared by all grid points, or ``(G, L, L)`` one per point.

    Returns
    -------
    GridSolution
        Estimates, moment residuals, criterion and ``invsym(A' W A)``.  A pivot that is too
        small is dropped by ``invsym`` exactly as in Mata, which sets the matching estimate
        to zero (for instance regime columns that are empty at an extreme threshold).
    """
    # Stata: GMM_cal (xthenreg.ado:1175)
    a = np.asarray(a, dtype=np.float64)
    y = np.asarray(y, dtype=np.float64)
    w = np.asarray(weight, dtype=np.float64)
    if a.ndim != 3 or y.shape != (a.shape[1],) or w.shape[-2:] != (a.shape[1],) * 2:
        raise ValueError("shapes of a, y and weight are inconsistent")
    if w.ndim == 3 and w.shape[0] != a.shape[0]:
        raise ValueError("a per-point weight needs one matrix per grid point")
    at = np.swapaxes(a, 1, 2)
    wa = np.matmul(w, a)
    bread = np.matmul(at, wa)
    wy = np.matmul(w, y)
    rhs = np.einsum("glp,gl->gp", a, wy) if wy.ndim == 2 else np.einsum("glp,l->gp", a, wy)
    bread_inv = invsym_batch(bread)
    theta = np.einsum("gpq,gq->gp", bread_inv, rhs)
    gbar = y[None, :] - np.einsum("glp,gp->gl", a, theta)
    w_gbar = np.einsum("gkl,gl->gk", w, gbar) if w.ndim == 3 else gbar @ w.T
    crit = np.einsum("gl,gl->g", gbar, w_gbar)
    return GridSolution(theta, gbar, crit, bread_inv)


def moment_covariance(g: FloatArray, center: bool = True) -> FloatArray:
    """Covariance of the unit moments, ``(1/N) sum g_i g_i' - (1/N^2) (sum g_i)(sum g_i)'``.

    This is the matrix whose inverse is the second-step weight (Mata: ``GMM_W_n_2_con``);
    ``center=False`` keeps only the uncentred second moment.

    Parameters
    ----------
    g
        Moments of each unit, ``(N, L)``.
    """
    # Stata: GMM_W_n_2_con (xthenreg.ado:1293)
    g = np.asarray(g, dtype=np.float64)
    n = g.shape[0]
    second = np.asarray(g.T @ g / n, dtype=np.float64)
    if not center:
        return second
    mean = g.sum(axis=0) / n
    return np.asarray(second - np.outer(mean, mean), dtype=np.float64)


# ------------------------------------------------------------ one equation system, fixed weight
#: Fewest stacked equations for which the estimator is computed.
MIN_EQUATIONS = 20


class FixedWeightFit(NamedTuple):
    """GMM at one threshold with a given weight matrix (``xdpt2_solve_gmm_1step_pre``).

    Attributes
    ----------
    ok
        False when the system is rejected (too few equations, singular or non-finite).
    theta
        Estimates ``(p,)``; empty when ``ok`` is False.
    obj
        Criterion ``n * gbar' W gbar``.
    cov
        ``(A' W A)^{-1} / n`` with ``A = Z'X / n``, the variance if ``W`` were efficient.
    """

    ok: bool
    theta: FloatArray
    obj: float
    cov: FloatArray


_REJECTED = FixedWeightFit(False, np.empty(0), float("nan"), np.empty((0, 0)))


def solve_fixed_weight(
    zw: FloatArray, zy: FloatArray, weight: FloatArray, n_rows: int
) -> FixedWeightFit:
    """Linear GMM with a fixed weight matrix from the moment cross products.

    Parameters
    ----------
    zw
        ``Z'X / n``, ``(L, p)``.
    zy
        ``Z'y / n``, ``(L,)``.
    weight
        Weight matrix ``(L, L)``.
    n_rows
        Number of stacked equations ``n``.
    """
    # Stata: xdpt2_solve_gmm_1step_pre (xtdpthresh.ado:3917)
    if n_rows < MIN_EQUATIONS or weight.shape != (zw.shape[0], zw.shape[0]):
        return _REJECTED
    w_zw = weight @ zw
    bread = syminv(zw.T @ w_zw)
    if not bread.ok:
        return _REJECTED
    theta = bread.inv @ (w_zw.T @ zy)
    gbar = zy - zw @ theta
    obj = float(n_rows * (gbar @ (weight @ gbar)))
    cov = bread.inv / n_rows
    if not (np.all(np.isfinite(theta)) and np.all(np.isfinite(gbar)) and np.isfinite(obj)):
        return _REJECTED
    if not np.all(np.isfinite(cov)):
        return _REJECTED
    return FixedWeightFit(True, theta, obj, cov)


def cluster_omega(moments: FloatArray, n_rows: int, n_clusters: int, center: bool) -> FloatArray:
    """Cluster covariance of the moments, ``(1/n) sum_i g_i g_i'``, centred or not.

    The scaling is by the number of equations ``n``, not by the number of clusters.  With
    ``center`` the outer product of the mean moment is subtracted:
    ``sum_i (g_i - s/m)(g_i - s/m)' = sum_i g_i g_i' - s s' / m`` with ``m`` the clusters that
    contribute.

    Parameters
    ----------
    moments
        ``g_i = sum_{e in unit i} z_e * resid_e``, ``(n_units, L)``; units without equations
        are zero rows and change nothing.
    n_rows
        Number of stacked equations.
    n_clusters
        Units that have at least one stacked equation.
    center
        Subtract the mean-moment outer product.
    """
    # Stata: xdpt2_build_cluster_omega_c (xtdpthresh.ado:4012)
    if not np.all(np.isfinite(moments)):
        return np.full((moments.shape[1],) * 2, np.nan)
    omega = np.asarray(moments.T @ moments / n_rows)
    if center:
        total = moments.sum(axis=0)
        omega = omega - np.outer(total, total) / (n_clusters * n_rows)
    return omega


def sandwich(
    zw: FloatArray, weight: FloatArray, omega: FloatArray, n_rows: int
) -> FloatArray | None:
    """Robust variance ``B (D' A Omega A D) B / n`` with ``D = Z'X / n`` and ``B = (D' A D)^{-1}``.

    Valid for any fixed weight ``A``, efficient or not.  ``None`` when the bread cannot be
    inverted or the result is not finite.
    """
    # Stata: xdpt2_gmm_sandwich (xtdpthresh.ado:4048)
    if weight.shape != omega.shape:
        return None
    w_zw = weight @ zw
    bread = syminv(zw.T @ w_zw)
    if not bread.ok:
        return None
    meat = w_zw.T @ omega @ w_zw
    if not np.all(np.isfinite(meat)):
        return None
    cov = bread.inv @ meat @ bread.inv / n_rows
    return cov if bool(np.all(np.isfinite(cov))) else None
