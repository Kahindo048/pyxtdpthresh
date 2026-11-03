"""Fixed-weight GMM criteria of many candidate models on many bootstrap samples.

Every bootstrap statistic of the command compares the one-step criterion of a *restricted* model
with the smallest criterion of the *unrestricted* candidates, on samples ``Y* = F + E`` made of a
fitted part ``F`` and reweighted residuals ``E``.  With a fixed weight ``W`` the criterion of a
candidate depends on the sample only through the moments ``m* = Z'Y*/n``:

    theta = C m*,     g = m* - ZW theta = (I - ZW C) m*,     J = n g'W g,

with ``ZW = Z'X/n`` and ``C = (ZW'W ZW)^{-1} ZW'W`` fixed per candidate.  The moments of the
samples are ``m*_b = ZF + (sum_i eta_ib g_i) / n`` where ``g_i`` is the moment contribution of
unit ``i`` to ``Z'resid``: no ``n x B`` matrix is ever formed, and all candidates and replications
are evaluated with a few matrix products.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from pyxtdpthresh._types import BoolArray, FloatArray
from pyxtdpthresh.core.linalg import objtol, syminv

#: Largest number of elements of the ``(candidates, L, B)`` work array.
CHUNK_ELEMENTS = 8_000_000
#: Largest number of elements of the quadratic forms ``(candidates, L, L)`` kept per family.
QUADRATIC_ELEMENTS = 40_000_000


@dataclass(frozen=True)
class Family:
    """Solvers of the candidates under one fixed weight.

    Attributes
    ----------
    zw
        ``Z'X/n`` of each candidate, ``(G, L, p)`` (zeros where the candidate is not solvable).
    solver
        ``C`` of each candidate, ``(G, p, L)`` (zeros where the candidate is not solvable).
    solvable
        The normal matrix ``ZW'W ZW`` is admitted and ``C`` is finite.
    weight
        The weight.
    quadratic
        ``M'W M`` with ``M = I - ZW C`` of each candidate, ``(G, L, L)``: the criterion of a
        sample is then ``n m*'(M'W M) m*``.  ``None`` when it would take too much memory.
    """

    zw: FloatArray
    solver: FloatArray
    solvable: BoolArray
    weight: FloatArray
    quadratic: FloatArray | None = None

    @property
    def size(self) -> int:
        """Number of candidates."""
        return int(self.solvable.size)

    def take(self, index: np.ndarray) -> Family:
        """Sub-family of the candidates ``index``."""
        quadratic = None if self.quadratic is None else self.quadratic[index]
        return Family(
            self.zw[index], self.solver[index], self.solvable[index], self.weight, quadratic
        )


def make_family(zw: list[FloatArray | None], weight: FloatArray, n_params: int) -> Family:
    """Build the solvers of the candidates ``zw`` (``None`` for a candidate that does not exist)."""
    # Stata: xdpt2_build_gamma_cache_t (C_g, xtdpthresh.ado:4597), xdpt2_cache_w2 (6647)
    n_moments = weight.shape[0]
    count = len(zw)
    zws = np.zeros((count, n_moments, n_params))
    solver = np.zeros((count, n_params, n_moments))
    solvable = np.zeros(count, dtype=np.bool_)
    for g, moments in enumerate(zw):
        if moments is None:
            continue
        zws[g] = moments
        if n_params == 0:
            solvable[g] = True
            continue
        w_zw = weight @ moments
        bread = syminv(moments.T @ w_zw)
        if not bread.ok:
            continue
        c = bread.inv @ w_zw.T
        if np.all(np.isfinite(c)):
            solver[g] = c
            solvable[g] = True
    quadratic = None
    if count * n_moments * n_moments <= QUADRATIC_ELEMENTS:
        m = np.eye(n_moments)[None] - np.matmul(zws, solver)
        quadratic = np.matmul(m.transpose(0, 2, 1), np.matmul(weight, m))
        quadratic = (quadratic + quadratic.transpose(0, 2, 1)) / 2.0
    return Family(zws, solver, solvable, weight, quadratic)


def criterion(
    family: Family, moments: FloatArray, n_rows: int, index: np.ndarray | None = None
) -> FloatArray:
    """One-step criterion ``n g'W g`` of the candidates on samples with moments ``m*``.

    Parameters
    ----------
    family
        Candidates and their weight.
    moments
        ``m* = Z'Y*/n`` of each sample, ``(L, B)``.
    n_rows
        Number of stacked equations ``n``.
    index
        Candidates to evaluate (default all).

    Returns
    -------
    numpy.ndarray
        ``(len(index), B)``; ``nan`` where the candidate is not solvable or a term is not finite.
    """
    # Stata: xdpt2_fast_obj_split_list (xtdpthresh.ado:4668), in cross-product form
    chosen = np.arange(family.size) if index is None else np.asarray(index, dtype=np.int64)
    n_samples = moments.shape[1]
    out = np.full((chosen.size, n_samples), np.nan)
    n_moments = moments.shape[0]
    step = max(1, CHUNK_ELEMENTS // max(1, n_moments * n_samples))
    for start in range(0, chosen.size, step):
        part = chosen[start : start + step]
        size = part.size
        if family.quadratic is not None:
            by_moment = family.quadratic[part].reshape(size * n_moments, n_moments) @ moments
            value = n_rows * np.einsum("glb,lb->gb", by_moment.reshape(size, n_moments, n_samples),
                                       moments)  # fmt: skip
        else:
            n_params = family.zw.shape[2]
            theta = (family.solver[part].reshape(size * n_params, n_moments) @ moments).reshape(
                size, n_params, n_samples
            )
            g = moments[None, :, :] - np.matmul(family.zw[part], theta)
            wg = np.matmul(family.weight, g)
            value = n_rows * np.sum(g * wg, axis=1)
        value[~np.isfinite(value)] = np.nan
        value[~family.solvable[part]] = np.nan
        out[start : start + step] = value
    return out


def sample_moments(
    fit_moments: FloatArray, unit_moments: FloatArray, weights: FloatArray, n_rows: int
) -> FloatArray:
    """Moments ``Z'Y*/n`` of the samples ``Y* = F + resid * eta[unit]``, ``(L, B)``.

    Parameters
    ----------
    fit_moments
        ``Z'F/n``, ``(L,)``.
    unit_moments
        ``g_i = sum of z_e resid_e`` over the equations of each unit, ``(n_units, L)``.
    weights
        Bootstrap weight of each unit in each sample, ``(n_units, B)``.
    n_rows
        Number of stacked equations.
    """
    # Stata: ZE = gsum_by_unit(Z :* R)' * ETA / n, ZF = Z'F / n (xtdpthresh.ado:4691)
    return np.asarray(fit_moments[:, None] + (unit_moments.T @ weights) / n_rows)


def critical_value(statistics: FloatArray, level_share: float) -> float:
    """Order statistic of rank ``ceil(p (n + 1))`` of the valid bootstrap statistics.

    ``accept iff D <= crit`` is then the add-one rule ``(1 + #{D* >= D}) / (1 + n) > 1 - p``.  No
    finite value (``inf``) when the rank exceeds ``n``: no draw can reject.  ``nan`` without
    valid statistics.
    """
    # Stata: xdpt2_crit_orderstat (xtdpthresh.ado:4839)
    values = np.sort(statistics[np.isfinite(statistics)])
    n = values.size
    if n == 0:
        return math.nan
    rank = max(1, math.ceil(level_share * (n + 1) - 1e-9))
    return math.inf if rank > n else float(values[rank - 1])


def profile_min(values: FloatArray, gammas: FloatArray) -> tuple[int, int, float]:
    """Return the index of the smallest finite value, how many there are and the largest.

    Ties (relative ``1e-12``) go to the smaller threshold.
    """
    # Stata: running argmin with xdpt2_objtol(.., 1e-12) in xdpt2_coef_bootstrap
    best, count, high = -1, 0, math.nan
    for i in np.flatnonzero(np.isfinite(values)):
        value = float(values[i])
        count += 1
        if math.isnan(high) or value > high:
            high = value
        if best < 0:
            best = int(i)
            continue
        tol = objtol(value, float(values[best]), 1e-12)
        if value < values[best] - tol or (
            abs(value - values[best]) <= tol and gammas[i] < gammas[best]
        ):
            best = int(i)
    return best, count, high


def is_degenerate(low: float, high: float, count: int) -> bool:
    """Return whether the profile has fewer than two points or is flat."""
    if count < 2:
        return True
    scale = max(abs(low), abs(high))
    return abs(high - low) <= 1e-12 * scale
