"""Threshold search of ``xtdpthresh``: two stages over one grid, with optional local refinement.

1. **Stage 1** profiles the criterion over the grid with the first-step weight ``W1`` and keeps
   the best threshold.
2. The residuals of that fit give ``Omega`` and the second-step weight ``W2``, built **once**.
3. **Stage 2** profiles the criterion over the same grid with that fixed ``W2``.  The estimate
   is the stage-2 minimiser; its variance is the sandwich of ``W2`` with ``Omega`` rebuilt from
   the final residuals.
4. ``refine(#)`` then adds, for the jump model, the observed values of ``q`` that lie between the
   two neighbours of the stage-2 minimiser, 30 at a time, under the same ``W2``.  For the kink
   model the continuous criterion is minimised between those neighbours instead.

When ``Omega`` cannot be inverted, or the stage-2 profile is flat, the estimator stays at one step
(``twostep=False``) and reports the stage-1 fit with its sandwich.  A candidate is *admitted* when
it leaves at least the minimum number of observations on each side and its GMM system is solved.
Ties go to the smaller threshold (a relative tolerance of ``1e-12`` on the criterion).
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np

from pyxtdpthresh._errors import DataError
from pyxtdpthresh._i18n import message
from pyxtdpthresh._types import FloatArray, GridType
from pyxtdpthresh.core.gmm import sandwich, solve_fixed_weight
from pyxtdpthresh.core.grids import ThresholdGrid, admissible, threshold_grid
from pyxtdpthresh.core.linalg import objtol
from pyxtdpthresh.models.xtdpthresh.estimator import (
    ThresholdFit,
    omega_of,
    problem_at,
    second_step_weight,
)
from pyxtdpthresh.models.xtdpthresh.sample import MIN_UNITS
from pyxtdpthresh.models.xtdpthresh.stack import Stack

#: Relative tolerance on the criterion to call two thresholds tied.
TIE_TOL = 1e-12
#: Candidates added per ``refine`` round.
REFINE_BATCH = 30
#: Rounds and points of the kink refinement: first 40 points between the neighbours, then 10.
KINK_ROUNDS, KINK_FIRST, KINK_NEXT = 8, 40, 10


@dataclass
class _Best:
    """Running minimiser of a profile."""

    index: int = -1
    obj: float = math.nan
    gamma: float = math.nan
    theta: FloatArray = field(default_factory=lambda: np.empty(0))
    obj_hi: float = math.nan
    n_admitted: int = 0
    admitted: list[float] = field(default_factory=list)

    @property
    def found(self) -> bool:
        return self.index >= 0

    @property
    def flat(self) -> bool:
        """Fewer than two admitted points, or a maximum equal to the minimum."""
        # Stata: xdpt2_profile_is_flat (xtdpthresh.ado:5456)
        if not self.found or math.isnan(self.obj_hi) or self.n_admitted < 2:
            return True
        scale = max(abs(self.obj), abs(self.obj_hi))
        return scale == 0 or abs(self.obj_hi - self.obj) <= TIE_TOL * scale


def _better(obj: float, gamma: float, best_obj: float, best_gamma: float) -> bool:
    """Lower criterion beyond the tolerance, or a tie at a smaller threshold."""
    tol = objtol(obj, best_obj, TIE_TOL)
    return obj < best_obj - tol or (abs(obj - best_obj) <= tol and gamma < best_gamma)


class ThresholdCache:
    """Moments ``Z'X(gamma) / n`` of the candidate thresholds, in the order they were added."""

    def __init__(self, stack: Stack, support: FloatArray, min_regime: int) -> None:
        self.stack = stack
        self.support = support
        self.min_regime = min_regime
        self.gammas: FloatArray = np.empty(0)
        self.zw: list[FloatArray | None] = []

    def _structural(self, gammas: FloatArray) -> np.ndarray:
        """Admission before any solve: regime sizes and at least one more moment than parameters."""
        # Stata: xdpt2_build_gamma_cache_t (xtdpthresh.ado:4484-4508)
        k = self.stack.zdx.shape[1]
        n_parameters = k + 1 if self.stack.kink else 2 * k + 1
        wide_enough = self.stack.n_instruments >= n_parameters + 1
        ok = admissible(gammas, self.support, self.min_regime)
        return ok if wide_enough else np.zeros_like(ok)

    def add(self, candidates: FloatArray) -> tuple[int, int]:
        """Append the candidates not yet present; return the range ``[first, last)`` added."""
        new = np.unique(candidates[np.isfinite(candidates)])
        new = new[~np.isin(new, self.gammas)]
        if new.size == 0:
            return 0, 0
        ok = self._structural(new)
        moments = self.stack.moments(new[ok]) if ok.any() else None
        entries: list[FloatArray | None] = [None] * new.size
        for slot, position in enumerate(np.flatnonzero(ok)):
            entries[position] = moments[slot] if moments is not None else None
        first = self.gammas.size
        self.gammas = np.concatenate([self.gammas, new])
        self.zw.extend(entries)
        return first, self.gammas.size

    def append_entry(self, gamma: float, moments: FloatArray) -> int:
        """Append one evaluated candidate and return its index."""
        self.gammas = np.append(self.gammas, gamma)
        self.zw.append(moments)
        return self.gammas.size - 1

    def profile(
        self, best: _Best, first: int, last: int, weight: FloatArray, *, count: bool = True
    ) -> None:
        """Evaluate the entries ``first:last`` under ``weight`` and update the running minimiser."""
        # Stata: xdpt2_profile_update (xtdpthresh.ado:5386)
        stack = self.stack
        for i in range(first, last):
            moments = self.zw[i]
            if moments is None:
                continue
            fit = solve_fixed_weight(moments, stack.zy, weight, stack.n_rows)
            if not fit.ok:
                continue
            gamma = float(self.gammas[i])
            if count:
                best.n_admitted += 1
                best.admitted.append(gamma)
                if math.isnan(best.obj_hi) or fit.obj > best.obj_hi:
                    best.obj_hi = fit.obj
            if not best.found or _better(fit.obj, gamma, best.obj, best.gamma):
                best.index, best.obj, best.gamma, best.theta = i, fit.obj, gamma, fit.theta

    def like(self) -> ThresholdCache:
        """Empty cache with the same stack, support and floor."""
        return ThresholdCache(self.stack, self.support, self.min_regime)


@dataclass(frozen=True)
class RefineStats:
    """Bookkeeping of ``refine(#)``."""

    iterations: int
    added: int
    pool: int
    remaining: float
    complete: bool
    neighbours_remaining: float
    in_basin: bool
    objective_gain: float


@dataclass(frozen=True)
class SearchResult:
    """Outcome of the threshold search.

    Attributes
    ----------
    fit
        Final estimate (second step unless the estimator fell back to one step).
    stage1_gamma, stage1_obj
        Threshold and criterion that built the second-step weight.
    grid
        Every candidate threshold evaluated, the initial grid first.
    grid_requested, grid_effective, grid_admitted
        Requested points, evaluated points, and points admitted in stage 1 (``e(grid_admitted)``).
    admitted_lo, admitted_hi
        Smallest and largest stage-1 admitted threshold.
    admitted_2
        Points admitted in stage 2.
    q_lo, q_hi
        Trimmed bounds of the threshold variable on the effective support.
    min_regime
        Floor on the regime size actually applied.
    kink_refined
        The kink refinement moved the estimate off the grid.
    refine
        Statistics of ``refine(#)`` (``None`` when it was not requested or not applied).
    cache
        Moments of every candidate threshold, in the order of ``grid`` (the bootstraps replay the
        search over the first ``n_stage1`` entries).
    n_stage1
        Number of initial-grid candidates, the set both stages searched.
    stage2_global_obj
        Smallest second-step criterion over the initial grid, before ``refine`` (``nan`` after a
        one-step fallback).
    """

    fit: ThresholdFit
    stage1_gamma: float
    stage1_obj: float
    grid: FloatArray
    grid_requested: int
    grid_effective: int
    grid_admitted: int
    admitted_lo: float
    admitted_hi: float
    admitted_2: int
    q_lo: float
    q_hi: float
    min_regime: int
    kink_refined: bool
    refine: RefineStats | None
    cache: ThresholdCache
    n_stage1: int
    stage2_global_obj: float


def threshold_support(stack: Stack, observed: bool) -> tuple[FloatArray, FloatArray]:
    """Values of ``q`` that define the grid, and those that define the realised regime split.

    The effective support is the ``q`` of every level observation that enters a stacked equation
    (``t`` and ``t - 1``); ``observed`` keeps only the current-row values, as ``xthenreg`` does.
    """
    # Stata: xdpt2_q_support (xtdpthresh.ado:2744) and gridsample(observed)
    levels = stack.level_support
    split = stack.level_q[levels]
    split = np.unique(split[np.isfinite(split)])
    if observed:
        current = stack.level_q[np.unique(stack.current_level)]
        return current[np.isfinite(current)], split
    every = stack.level_q[levels]
    return every[np.isfinite(every)], split


def _kink_refine(
    cache: ThresholdCache, best: _Best, anchors: list[float], weight: FloatArray
) -> bool:
    """Minimise the continuous criterion between the neighbours of the grid minimiser."""
    # Stata: xdpt2_kink_refine (xtdpthresh.ado:5516)
    if not best.found or not np.isfinite(best.gamma) or not anchors:
        return False
    points = np.unique(np.asarray(anchors))
    hit = np.flatnonzero(points == best.gamma)
    if hit.size == 0:
        return False
    pos = int(hit[-1])
    lo = float(points[pos - 1]) if pos > 0 else float(np.min(cache.gammas))
    hi = float(points[pos + 1]) if pos < points.size - 1 else float(np.max(cache.gammas))
    if not hi > lo:
        return False
    tol = 1e-6 * (hi - lo)
    r_obj, r_gamma = best.obj, best.gamma
    keep: tuple[float, FloatArray] | None = None
    lower, upper, count = lo, hi, KINK_FIRST
    for _ in range(KINK_ROUNDS):
        spacing = (upper - lower) / (count + 1)
        trial = cache.like()
        first, last = trial.add(
            np.asarray(lower + spacing * np.arange(1, count + 1), dtype=np.float64)
        )
        found = _Best()
        trial.profile(found, first, last, weight)
        if found.found and _better(found.obj, found.gamma, r_obj, r_gamma):
            r_obj, r_gamma = found.obj, found.gamma
            moments = trial.zw[found.index]
            assert moments is not None
            keep = (r_gamma, moments)
        if spacing <= tol:
            break
        lower, upper, count = max(lo, r_gamma - spacing), min(hi, r_gamma + spacing), KINK_NEXT
    if keep is None:
        return False
    j = cache.append_entry(*keep)
    cache.profile(best, j, j + 1, weight, count=False)
    return best.index == j


def _refine_jump(
    cache: ThresholdCache,
    best: _Best,
    split: FloatArray,
    rounds: int,
    weight: FloatArray,
    global_obj: float,
) -> RefineStats | None:
    """Add observed values of ``q`` between the neighbours of the stage-2 minimiser."""
    # Stata: final jump-only local refinement (xtdpthresh.ado:6045-6192)
    grid_lo, grid_hi = float(np.min(cache.gammas)), float(np.max(cache.gammas))
    anchors = np.unique(np.asarray(best.admitted))
    hit = np.flatnonzero(anchors == best.gamma)
    if split.size == 0 or anchors.size < 2 or hit.size == 0:
        return None
    pos = int(hit[-1])
    lo = float(anchors[pos - 1]) if pos > 0 else grid_lo
    hi = float(anchors[pos + 1]) if pos < anchors.size - 1 else grid_hi
    pool = split[(split > lo) & (split < hi)]
    pool = pool[~np.isin(pool, cache.gammas)]
    pool_size, iterations, added = int(pool.size), 0, 0
    while iterations < rounds:
        candidates = pool[~np.isin(pool, cache.gammas)]
        if candidates.size == 0:
            break
        if candidates.size > REFINE_BATCH:
            picks = np.unique(
                np.floor(np.arange(REFINE_BATCH) * ((candidates.size - 1) / (REFINE_BATCH - 1)))
            ).astype(np.int64)
            candidates = candidates[picks]
        first, last = cache.add(candidates)
        if first == last:
            break
        added += last - first
        iterations += 1
        cache.profile(best, first, last, weight)
    remaining = float(np.sum(~np.isin(pool, cache.gammas)))
    final = np.unique(np.asarray(best.admitted))
    where = np.flatnonzero(final == best.gamma)
    neighbours = math.nan
    complete = False
    if final.size >= 2 and where.size:
        f = int(where[-1])
        near_lo = float(final[f - 1]) if f > 0 else grid_lo
        near_hi = float(final[f + 1]) if f < final.size - 1 else grid_hi
        inside = split[(split > near_lo) & (split < near_hi)]
        neighbours = float(np.sum(~np.isin(inside, cache.gammas)))
        complete = remaining == 0 and neighbours == 0
    scale = max(abs(global_obj), abs(best.obj))
    gain = 0.0 if scale == 0 else max((global_obj - best.obj) / scale, 0.0)
    if best.obj > global_obj + objtol(best.obj, global_obj, 1e-10):
        raise RuntimeError("internal refinement error: fixed-W2 objective increased")
    return RefineStats(
        iterations, added, pool_size, remaining, complete, neighbours, lo <= best.gamma <= hi, gain
    )


def _failure(best: _Best) -> DataError:
    """No admitted threshold, or a criterion that does not vary over the admitted ones."""
    key = "xd_profile_flat" if best.n_admitted >= 2 else "xd_no_gamma"
    return DataError(message(key), stata_code=498, key=key)


def _final_variance(
    stack: Stack, cache: ThresholdCache, index: int, theta: FloatArray, weight: FloatArray,
    *, center: bool,
) -> FloatArray:  # fmt: skip
    """Sandwich of ``weight`` with ``Omega`` rebuilt from the residuals at ``theta``."""
    moments = cache.zw[index]
    assert moments is not None
    gamma = float(cache.gammas[index])
    resid = stack.dy - stack.regressors(gamma) @ theta
    omega = omega_of(stack, resid, center=center)
    cov = sandwich(moments, weight, omega, stack.n_rows)
    if cov is None:
        raise DataError(message("xd_variance_failed"), stata_code=498, key="xd_variance_failed")
    return cov


def search_threshold(
    stack: Stack,
    *,
    grid: int,
    grid_type: GridType = "uniform",
    observed_support: bool = False,
    trim: float = 0.10,
    min_regime: int = 0,
    refine: int = 0,
    center: bool = True,
    grid_values: FloatArray | None = None,
) -> SearchResult:
    """Two-stage search of the threshold and the estimate at the minimiser.

    Parameters
    ----------
    stack
        First-difference system, from :func:`build_stack`.
    grid, grid_type
        Number of grid points and their placement (uniform or on quantiles).
    observed_support
        Build the grid from the current-row values of ``q`` only (``gridsample(observed)``).
    trim, min_regime
        Total trimmed share and ``minregime()``.
    refine
        Rounds of local refinement (jump model).
    center
        Centre the covariance of the moments.
    grid_values
        Candidate thresholds to use instead of the grid built from ``grid`` and ``grid_type``
        (``grid`` then only counts the requested points).

    Raises
    ------
    DataError
        If the threshold variable has no usable support, fewer than five units contribute, no
        threshold is admitted or the criterion is flat on the admitted grid (return code 498).
    """
    # Stata: xtdpthresh_run (xtdpthresh.ado:8808-9041) and xdpt2_grid_search (5630)
    support, split = threshold_support(stack, observed_support)
    spec = threshold_grid(support, trim, grid, grid_type, min_regime)
    if stack.n_units < MIN_UNITS:
        raise DataError(
            message("xd_few_units", n=stack.n_units), stata_code=498, key="xd_few_units"
        )
    cache = ThresholdCache(stack, support, spec.min_regime)
    cache.add(spec.grid if grid_values is None else np.asarray(grid_values, dtype=np.float64))
    n_grid = cache.gammas.size

    one = _Best()
    cache.profile(one, 0, n_grid, stack.first_weight.weight)
    if not one.found or one.flat:
        raise _failure(one)
    admitted_1 = list(one.admitted)
    stage1_gamma, stage1_obj = one.gamma, one.obj

    step = problem_at(stack, one.gamma)
    _, weight_2 = second_step_weight(stack, step, one.theta, center=center)
    two = _Best()
    if weight_2 is not None:
        cache.profile(two, 0, n_grid, weight_2)
    if weight_2 is None or not two.found or two.flat:
        # the estimator stays at one step: stage-1 fit with the sandwich of W1
        refined = stack.kink and _kink_refine(cache, one, admitted_1, stack.first_weight.weight)
        cov = _final_variance(
            stack, cache, one.index, one.theta, stack.first_weight.weight, center=center
        )
        fit = ThresholdFit(
            one.gamma, one.theta, one.obj, cov, stack.first_weight.weight, False, one.theta, one.obj
        )  # fmt: skip
        return _result(
            fit, cache, spec, grid, admitted_1, stage1_gamma, stage1_obj, 0, refined, None,
            n_grid, math.nan,
        )  # fmt: skip

    global_obj = two.obj
    stats = None
    if refine > 0:
        stats = _refine_jump(cache, two, split, refine, weight_2, two.obj)
    refined = stack.kink and _kink_refine(cache, two, list(two.admitted), weight_2)
    cov = _final_variance(stack, cache, two.index, two.theta, weight_2, center=center)
    fit = ThresholdFit(two.gamma, two.theta, two.obj, cov, weight_2, True, one.theta, one.obj)
    return _result(
        fit, cache, spec, grid, admitted_1, stage1_gamma, stage1_obj, two.n_admitted, refined,
        stats, n_grid, global_obj,
    )  # fmt: skip


def _result(
    fit: ThresholdFit,
    cache: ThresholdCache,
    spec: ThresholdGrid,
    requested: int,
    admitted_1: list[float],
    stage1_gamma: float,
    stage1_obj: float,
    admitted_2: int,
    kink_refined: bool,
    stats: RefineStats | None,
    n_stage1: int,
    stage2_global_obj: float,
) -> SearchResult:
    return SearchResult(
        fit, stage1_gamma, stage1_obj, cache.gammas, requested, int(cache.gammas.size),
        len(admitted_1), min(admitted_1), max(admitted_1), admitted_2, spec.q_lo, spec.q_hi,
        spec.min_regime, kink_refined, stats, cache, n_stage1, stage2_global_obj,
    )  # fmt: skip
