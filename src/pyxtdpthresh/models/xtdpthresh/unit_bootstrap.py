"""Unit-resampling bootstrap of the confidence set (``boot_type="unit"``).

The structure of Algorithm 1 of Gong and Seo: units are resampled with replacement, the data
generating process uses the **restricted** coefficients at the candidate threshold but the
**unrestricted** residuals at the estimate, the bootstrap moments are recentred at the sample
moment, and the weight is re-estimated in every draw.  Per draw:

1. the first-step coefficients are re-estimated on every grid point with ``W1``, and the best one
   gives residuals whose recentred cluster covariance ``Omega*`` defines ``W2* = Omega*^{-1}``;
2. the criterion is evaluated at the candidate (restricted) and at every grid point (unrestricted)
   with ``W2*``; the distance is ``J_restricted - min(J_restricted, min J_unrestricted)``.

A resample is a vector of unit counts, so every quantity is a sum over units of per-unit
cross products that do not depend on the draw: ``Z'X_g`` of each grid point, ``Z'y`` and the unit
moments.  A draw then costs a few small matrix products and no pass over the ``n`` equations.
It is an experimental extension beyond the common-T theory; the command says so.
"""

from __future__ import annotations

import numpy as np

from pyxtdpthresh._types import FloatArray
from pyxtdpthresh.core.linalg import syminv_batch
from pyxtdpthresh.inference.bootstrap.draws import BootstrapStreams
from pyxtdpthresh.inference.bootstrap.objective import usable_minimum
from pyxtdpthresh.models.xtdpthresh.estimator import contributing_moments
from pyxtdpthresh.models.xtdpthresh.stack import Stack

#: Draws processed together (they share the work arrays).
CHUNK = 64
#: Fewest resampled equations for a draw to be usable.
MIN_RESAMPLED_ROWS = 20


def unit_cross_products(stack: Stack, regressors: FloatArray) -> FloatArray:
    """``sum over the equations of unit i of z_e x_e'``, ``(n_units, L, p)``."""
    columns = [contributing_moments(stack, regressors[:, j]) for j in range(regressors.shape[1])]
    return np.stack(columns, axis=2)


class UnitResampler:
    """State shared by the draws of all candidates: grid cross products and sample moments.

    Parameters
    ----------
    stack
        System of the fit.
    gammas, moments
        Initial-grid candidates and their ``Z'X/n`` (``None`` for those not admitted).
    w1, w2
        First-step weight and the second-step weight of the fit.
    theta_hat, gamma_hat
        Estimate: the unrestricted residuals are taken at it.
    center
        Centre the covariance of the moments over the resampled units.
    """

    def __init__(
        self,
        stack: Stack,
        gammas: FloatArray,
        moments: list[FloatArray | None],
        w1: FloatArray,
        gamma_hat: float,
        theta_hat: FloatArray,
        center: bool,
    ) -> None:
        self.stack, self.w1, self.center = stack, w1, center
        self.index = [i for i, m in enumerate(moments) if m is not None]
        self.gammas = gammas[self.index]
        self.grid = np.stack(
            [unit_cross_products(stack, stack.regressors(float(g))) for g in self.gammas], axis=1
        )  # (n_units, G, L, p)
        resid_hat = stack.dy - stack.regressors(gamma_hat) @ theta_hat
        self.shat = stack.z.rmatmul(resid_hat)
        self.rhat = resid_hat
        has = np.diff(stack.unit_ptr) > 0
        self.rows = np.diff(stack.unit_ptr)[has].astype(np.float64)
        self.n_units = int(has.sum())

    def distances(
        self, streams: BootstrapStreams, component: str, candidate: float, theta: FloatArray,
        w2: FloatArray, n_boot: int,
    ) -> FloatArray:  # fmt: skip
        """Bootstrap distances of one candidate threshold, ``nan`` for the draws that fail."""
        # Stata: boottype(unit) branch of xdpt2_grid_bootstrap (xtdpthresh.ado:7013-7207)
        stack = self.stack
        regressors = stack.regressors(candidate)
        y_star = regressors @ theta + self.rhat
        sample = contributing_moments(stack, y_star)
        own = unit_cross_products(stack, regressors)
        rng = streams.stream(component)
        picks = np.floor(rng.uniform((n_boot, self.n_units)) * self.n_units).astype(np.int64)
        counts = np.zeros((n_boot, self.n_units))
        for draw in range(n_boot):
            counts[draw] = np.bincount(picks[draw], minlength=self.n_units)
        out: list[float] = []
        for start in range(0, n_boot, CHUNK):
            out.extend(self._chunk(counts[start : start + CHUNK], sample, own, w2))
        result = np.full(n_boot, np.nan)
        result[: len(out)] = out
        return result

    def _chunk(
        self, counts: FloatArray, sample: FloatArray, own: FloatArray, w2: FloatArray
    ) -> list[float]:
        """Distances of the valid draws of a chunk (invalid draws are skipped, as in Stata)."""
        # STATA-QUIRK: a draw whose profile has no usable minimum is skipped, not replaced, so the
        # chunk can return fewer distances than draws; the missing ones stay NaN in the result.
        w1 = self.w1
        size = counts.shape[0]
        rows = counts @ self.rows
        usable = rows >= MIN_RESAMPLED_ROWS
        y = counts @ sample - self.shat
        n_grid = self.grid.shape[1]
        n_moments, n_params = sample.shape[1], own.shape[2]
        zw = (counts @ self.grid.reshape(self.n_units, -1)).reshape(
            size, n_grid, n_moments, n_params
        )
        theta1, objective1 = self._solve(zw, y, w1, rows)
        best1, _, found1 = usable_minimum(objective1, self.gammas)
        picks = np.where(usable & found1, best1, -1)
        keep = np.flatnonzero(picks >= 0)
        if keep.size == 0:
            return []
        w2_star = self._reweight(
            counts[keep], sample, picks[keep], theta1[keep, picks[keep]], rows[keep]
        )
        valid = np.flatnonzero(np.isfinite(w2_star).all(axis=(1, 2)))
        if valid.size == 0:
            return []
        keep, w2_star = keep[valid], w2_star[valid]
        zw_own = np.einsum("bi,ilp->blp", counts[keep], own)
        restricted = _quadratic(zw_own[:, None], y[keep], w2_star, rows[keep])[:, 0]
        _, objective2 = self._solve(zw[keep], y[keep], w2_star, rows[keep])
        _, low2, found2 = usable_minimum(objective2, self.gammas)
        counted = found2 & np.isfinite(restricted)
        return [
            float(r - min(r, m)) for r, m in zip(restricted[counted], low2[counted], strict=True)
        ]

    def _solve(
        self, zw: FloatArray, y: FloatArray, weight: FloatArray, rows: FloatArray
    ) -> tuple[FloatArray, FloatArray]:
        """One-step estimates and criteria of every grid point in every draw."""
        return _grid_fit(zw, y, weight, rows)

    def _reweight(
        self, counts: FloatArray, sample: FloatArray, pick: np.ndarray, theta: FloatArray,
        rows: FloatArray,
    ) -> FloatArray:  # fmt: skip
        """``W2* = Omega*^{-1}`` from the recentred residual moments at the first-step argmin."""
        size, n_c = counts.shape
        n_moments = sample.shape[1]
        moments = np.empty((size, n_c, n_moments))
        for d in range(size):
            moments[d] = sample - np.einsum("ilp,p->il", self.grid[:, pick[d]], theta[d])
        moments -= self.shat[None, None, :] / n_c
        weighted = moments * counts[:, :, None]
        omega = np.einsum("bil,bim->blm", weighted, moments) / rows[:, None, None]
        if self.center:
            total = weighted.sum(axis=1)
            omega -= np.einsum("bl,bm->blm", total, total) / (n_c * rows)[:, None, None]
        omega = (omega + np.swapaxes(omega, 1, 2)) / 2.0
        ok, inverse = syminv_batch(omega)
        inverse[~ok] = np.nan
        return inverse


def _quadratic(zw: FloatArray, y: FloatArray, weight: FloatArray, rows: FloatArray) -> FloatArray:
    """Criterion ``m'W m / rows`` of the fit of ``y`` on ``ZW``, per draw and candidate."""
    _, objective = _grid_fit(zw, y, weight, rows)
    return objective


def _grid_fit(
    zw: FloatArray, y: FloatArray, weight: FloatArray, rows: FloatArray
) -> tuple[FloatArray, FloatArray]:
    """Fixed-weight GMM of every candidate in every draw (raw-sum moments).

    ``weight`` is one matrix ``(L, L)`` or one per draw ``(B, L, L)``.
    """
    w = weight if weight.ndim == 3 else np.broadcast_to(weight, (zw.shape[0], *weight.shape))
    w_zw = np.matmul(w[:, None], zw)
    normal = np.matmul(np.swapaxes(zw, 2, 3), w_zw)
    shape = normal.shape
    ok, inverse = syminv_batch(normal.reshape(-1, shape[2], shape[3]))
    inverse = inverse.reshape(shape)
    ok = ok.reshape(shape[:2])
    rhs = np.einsum("bglp,bl->bgp", w_zw, y)
    theta = np.einsum("bgpq,bgq->bgp", inverse, rhs)
    resid = y[:, None, :] - np.einsum("bglp,bgp->bgl", zw, theta)
    objective = np.einsum("bgl,bgl->bg", resid, np.einsum("blm,bgm->bgl", w, resid)) / rows[:, None]
    objective[~(ok & np.isfinite(objective) & np.isfinite(theta).all(axis=2))] = np.nan
    return theta, objective
