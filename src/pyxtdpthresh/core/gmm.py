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
from pyxtdpthresh.core.linalg import invsym_batch


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
