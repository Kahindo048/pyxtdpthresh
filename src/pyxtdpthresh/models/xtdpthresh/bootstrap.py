"""Bootstrap inference of ``xtdpthresh``: confidence set of the threshold and linearity test.

Both are *wild* cluster bootstraps with Mammen weights drawn once per unit, the same weights for
every candidate (common random numbers).  The statistics compare, on each sample, the criterion
of a restricted model with the smallest criterion of the threshold models over the initial grid:

* **linearity**: restricted = no regime (``delta = 0``); the p-value is
  ``(1 + #{D* >= D}) / (1 + B)`` (add-one rule);
* **confidence set**: for each candidate ``gamma_l`` of a grid, restricted = the model at
  ``gamma_l``; ``gamma_l`` is accepted when ``D <= crit``, the ``ceil((1 - alpha)(B + 1))``-th
  order statistic of the bootstrap distances.  The set is the inversion of the test.

The criterion is the one of the reported estimator: the second-step criterion with the fixed
weight ``W2`` after a two-step fit, the first-step criterion with ``W1`` after a one-step fallback.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, replace

import numpy as np

from pyxtdpthresh._errors import DataError
from pyxtdpthresh._i18n import message
from pyxtdpthresh._types import FloatArray, GridType
from pyxtdpthresh.core.gmm import solve_fixed_weight
from pyxtdpthresh.core.grids import threshold_grid
from pyxtdpthresh.core.linalg import objtol, syminv, syminv_batch
from pyxtdpthresh.core.quantiles import quantile_type7
from pyxtdpthresh.inference.bootstrap.draws import BootstrapStreams, mammen_weights
from pyxtdpthresh.inference.bootstrap.objective import (
    Family,
    criterion,
    critical_value,
    is_degenerate,
    make_family,
    profile_min,
    sample_moments,
)
from pyxtdpthresh.inference.bootstrap.progress import Progress
from pyxtdpthresh.models.xtdpthresh.estimator import contributing_moments, omega_of
from pyxtdpthresh.models.xtdpthresh.search import SearchResult, ThresholdCache
from pyxtdpthresh.models.xtdpthresh.stack import Stack
from pyxtdpthresh.models.xtdpthresh.unit_bootstrap import UnitResampler

#: Status of a candidate of the confidence set (column 6 of ``e(ci_grid)``).
VALID, MECHANICAL, NOT_ADMISSIBLE, SAMPLE_FAILED, FEW_DRAWS, NO_QUANTILE = 1, 2, 3, 4, 5, 6


@dataclass(frozen=True)
class Replay:
    """The search the bootstraps replay.

    Attributes
    ----------
    stack, search
        System and result of the search.
    weight
        Weight of the criterion: ``W2`` after a two-step fit, ``W1`` after a one-step fallback.
    twostep
        The reported estimator is two-step.
    family
        Solvers of the initial-grid candidates under ``weight``.
    n_params
        Number of parameters of the threshold model.
    """

    stack: Stack
    search: SearchResult
    weight: FloatArray
    twostep: bool
    family: Family
    n_params: int


def make_replay(stack: Stack, search: SearchResult) -> Replay:
    """Collect the pieces of the search that every bootstrap uses."""
    fit = search.fit
    weight = fit.weight if fit.twostep else stack.first_weight.weight
    entries = search.cache.zw[: search.n_stage1]
    n_params = stack.zdx.shape[1] + (1 if stack.kink else stack.zdx.shape[1] + 1)
    return Replay(
        stack, search, weight, fit.twostep, make_family(entries, weight, n_params), n_params
    )


def _alternative_minimum(values: FloatArray) -> FloatArray:
    """Smallest finite value per column, ``nan`` for a column without any."""
    finite = np.isfinite(values)
    filled = np.where(finite, values, np.inf)
    out = filled.min(axis=0) if values.shape[0] else np.full(values.shape[1], np.inf)
    out[~finite.any(axis=0)] = np.nan
    return np.asarray(out)


def _distances(restricted: FloatArray, alternative: FloatArray) -> FloatArray:
    """Return ``J_restricted - min(J_restricted, min alternatives)`` per sample (``nan`` if bad)."""
    low = np.fmin(restricted, alternative)
    distance = restricted - low
    bad = ~(np.isfinite(restricted) & np.isfinite(alternative) & np.isfinite(distance))
    distance[bad] = np.nan
    return np.asarray(distance)


# --------------------------------------------------------------------------------- linearity
@dataclass(frozen=True)
class LinearityTest:
    """Linearity test (``H0: delta = 0``).

    Attributes
    ----------
    p_value
        Bootstrap p-value, ``nan`` unless every draw is valid.
    statistic
        Sample distance ``D``.
    n_valid
        Valid draws (``e(boot_linearity_valid)``).
    """

    p_value: float
    statistic: float
    n_valid: int


def linearity_test(replay: Replay, streams: BootstrapStreams, n_boot: int) -> LinearityTest:
    """Wild bootstrap of the distance between the linear model and the best threshold model."""
    # Stata: xdpt2_linearity_test (xtdpthresh.ado:7768); the one-step weight W1 throughout
    stack, n = replay.stack, replay.stack.n_rows
    missing = LinearityTest(math.nan, math.nan, 0)
    w1 = stack.first_weight.weight
    entries = replay.search.cache.zw[: replay.search.n_stage1]
    grid = make_family(entries, w1, replay.n_params)
    k = stack.zdx.shape[1]
    zy = stack.zy
    if k == 0:
        theta = np.zeros(0)
        restricted_sample = float(n * (zy @ (w1 @ zy)))
    else:
        solved = solve_fixed_weight(stack.zdx, zy, w1, n)
        if not solved.ok:
            return missing
        theta, restricted_sample = solved.theta, solved.obj
    linear = make_family([stack.zdx], w1, k)
    if not linear.solvable[0] or not math.isfinite(restricted_sample):
        return missing
    sample = criterion(grid, zy[:, None], n)[:, 0]
    if not np.isfinite(sample).any():
        return missing
    statistic = restricted_sample - min(restricted_sample, float(np.nanmin(sample)))

    fit_part = stack.dx @ theta if k else np.zeros(n)
    resid = stack.dy - fit_part
    weights = mammen_weights(streams.stream("linearity"), stack.n_units, n_boot)
    moments = sample_moments(
        stack.z.rmatmul(fit_part) / n, contributing_moments(stack, resid), weights, n
    )
    restricted = criterion(linear, moments, n)[0]
    alternative = _alternative_minimum(criterion(grid, moments, n))
    distance = _distances(restricted, alternative)
    valid = int(np.isfinite(distance).sum())
    if valid < n_boot:
        return LinearityTest(math.nan, statistic, valid)
    exceed = int(np.sum(distance >= statistic))
    return LinearityTest((1 + exceed) / (1 + valid), statistic, valid)


# ---------------------------------------------------------------------------------- continuity
@dataclass(frozen=True)
class ContinuityTest:
    """Continuity test (``H0``: kink, against the jump model).

    Attributes
    ----------
    p_value
        Bootstrap p-value (``nan`` unless every draw is valid).
    statistic
        Sample distance ``T`` between the kink and the jump criteria.
    n_valid
        Valid draws (``e(boot_continuity_valid)``).
    n_common
        Thresholds where both models solve (``e(cont_common)``).
    """

    p_value: float
    statistic: float
    n_valid: int
    n_common: int


def _tie_break_best(
    objectives: list[tuple[float, float, int]],
) -> tuple[float, int] | None:
    """Smallest objective; ties (relative ``1e-12``) go to the smaller threshold."""
    best: tuple[float, float, int] | None = None
    for objective, gamma, position in objectives:
        if best is None:
            best = (objective, gamma, position)
            continue
        tol = objtol(objective, best[0], 1e-12)
        if objective < best[0] - tol or (abs(objective - best[0]) <= tol and gamma < best[1]):
            best = (objective, gamma, position)
    return None if best is None else (best[0], best[2])


def continuity_test(
    replay: Replay, support: FloatArray, streams: BootstrapStreams, n_boot: int, min_regime: int
) -> ContinuityTest:
    """Wild bootstrap of the distance between the kink and the jump criteria under the kink DGP.

    The restricted model is the continuous (kink) model at its best threshold of the initial grid;
    the bootstrap samples are its fit plus the *jump* residuals reweighted by unit.  Both models
    are compared with the criterion of the reported estimator, over the initial grid.
    """
    # Stata: xdpt2_continuity_test (xtdpthresh.ado:7431)
    stack, search, n = replay.stack, replay.search, replay.stack.n_rows
    nothing = ContinuityTest(math.nan, math.nan, 0, 0)
    n1 = search.n_stage1
    if n1 < 2:
        return nothing
    kink_stack = replace(stack, kink=True)
    cache = ThresholdCache(kink_stack, support, min_regime)
    cache.add(search.cache.gammas[:n1])
    n_kink = kink_stack.zdx.shape[1] + 1
    kink = make_family(cache.zw, replay.weight, n_kink)
    jump = replay.family
    gammas = search.cache.gammas[:n1]
    zy = stack.zy[:, None]
    kink_sample = criterion(kink, zy, n)[:, 0]
    jump_sample = criterion(jump, zy, n)[:, 0]
    common = np.flatnonzero(
        kink.solvable & jump.solvable & np.isfinite(kink_sample) & np.isfinite(jump_sample)
    )
    if common.size < 2:
        return ContinuityTest(math.nan, math.nan, 0, int(common.size))
    best = _tie_break_best([(float(kink_sample[i]), float(gammas[i]), int(i)) for i in common])
    assert best is not None
    kink_obj, k_index = best
    solvable_jump = np.flatnonzero(jump.solvable & np.isfinite(jump_sample))
    if solvable_jump.size == 0:
        return ContinuityTest(math.nan, math.nan, 0, int(common.size))
    j_index = int(solvable_jump[np.argmin(jump_sample[solvable_jump])])
    jump_obj = float(jump_sample[j_index])
    statistic = kink_obj - jump_obj
    if statistic < -objtol(kink_obj, jump_obj, 1e-10):
        return ContinuityTest(math.nan, math.nan, 0, int(common.size))
    statistic = max(statistic, 0.0)

    theta_kink = kink.solver[k_index] @ stack.zy
    theta_jump = jump.solver[j_index] @ stack.zy
    fitted = kink_stack.regressors(float(gammas[k_index])) @ theta_kink
    resid = stack.dy - stack.regressors(float(gammas[j_index])) @ theta_jump
    if not np.all(np.isfinite(resid)):
        return ContinuityTest(math.nan, statistic, 0, int(common.size))
    weights = mammen_weights(streams.stream("continuity"), stack.n_units, n_boot)
    draws = sample_moments(
        stack.z.rmatmul(fitted) / n, contributing_moments(stack, resid), weights, n
    )
    kink_obj_b = criterion(kink, draws, n, common)
    jump_obj_b = criterion(jump, draws, n, solvable_jump)
    position = {int(g): i for i, g in enumerate(solvable_jump)}
    for row, g in enumerate(common):
        kink_obj_b[row, ~np.isfinite(jump_obj_b[position[int(g)]])] = np.nan
    low_k, low_j = _alternative_minimum(kink_obj_b), _alternative_minimum(jump_obj_b)
    distance = low_k - low_j
    tolerance = 1e-10 * np.maximum(np.abs(low_k), np.abs(low_j))
    valid = (
        np.isfinite(low_k) & np.isfinite(low_j) & np.isfinite(distance) & (distance >= -tolerance)
    )
    count = int(valid.sum())
    if count < n_boot:
        return ContinuityTest(math.nan, statistic, count, int(common.size))
    exceed = int(np.sum(np.maximum(distance[valid], 0.0) >= statistic))
    return ContinuityTest((1 + exceed) / (1 + count), statistic, count, int(common.size))


# ------------------------------------------------------------------------- confidence set
@dataclass(frozen=True)
class ConfidenceSet:
    """Inversion of the grid-bootstrap test over a grid of candidate thresholds.

    Attributes
    ----------
    table
        One row per candidate: ``gamma, D, crit, accepted, n_valid, status`` (``e(ci_grid)``).
        Status: 1 valid, 2 mechanical accept (``D = 0``), 3 not admissible, 4 sample solve
        failed, 5 too few valid draws, 6 no quantile; 4 to 6 are unresolved, not rejections.
    segments
        Accepted runs ``[lower, upper]`` (``e(ci_segments)``).
    lo, hi
        Convex hull of the accepted set (``nan`` when empty or incomplete).
    empty, n_segments
        ``e(ci_empty)`` and ``e(ci_nseg)`` (``nan`` when the inversion is incomplete).
    n_admitted, grid_lo, grid_hi
        Candidates that passed the sample solve and the span they cover.
    n_evaluated
        Candidates with status 1 or 2.
    n_unresolved
        Candidates with status 4 to 6 (``e(ci_unresolved)``).
    min_valid
        Smallest number of valid draws over the candidates.
    """

    table: FloatArray
    segments: FloatArray
    lo: float
    hi: float
    empty: float
    n_segments: float
    n_admitted: int
    grid_lo: float
    grid_hi: float
    n_evaluated: int
    n_unresolved: int
    min_valid: float

    @property
    def grid(self) -> FloatArray:
        """The candidates."""
        return np.asarray(self.table[:, 0])

    @property
    def incomplete(self) -> float:
        """1 if some candidate is unresolved (``e(ci_incomplete)``)."""
        return float(self.n_unresolved > 0)

    @property
    def boundary_warn(self) -> int:
        """0 neither bound, 1 lower, 2 upper, 3 both bounds sit at an edge of the candidates."""
        # Stata: _bwarn (xtdpthresh.ado:1628-1642)
        span = self.grid_hi - self.grid_lo
        if not (math.isfinite(self.lo) and math.isfinite(self.hi) and span > 0):
            return 0
        eps = 1e-4 * span
        low = abs(self.lo - self.grid_lo) < eps
        high = abs(self.hi - self.grid_hi) < eps
        return 3 if (low and high) else (1 if low else (2 if high else 0))


def confidence_grid(
    replay: Replay, support: FloatArray, *, trim: float, n_grid: int, grid_type: GridType,
    min_regime: int, exact: bool = False,
) -> FloatArray:  # fmt: skip
    """Candidates of the confidence set: a grid over the trimmed range plus the estimate.

    After a one-step fallback the first-step argmin over the estimation grid is added as well, so
    that the set contains the point where the statistic is exactly zero.
    """
    # Stata: gamma_ci_grid (xtdpthresh.ado:9132-9171)
    stack, search = replay.stack, replay.search
    grid = threshold_grid(support, trim, n_grid, grid_type, min_regime).grid
    extra = [search.fit.gamma]
    if not replay.twostep and not exact:
        best, best_gamma = math.inf, math.nan
        for gamma, moments in zip(
            search.cache.gammas[: search.n_stage1], search.cache.zw[: search.n_stage1], strict=True
        ):
            if moments is None:
                continue
            solved = solve_fixed_weight(moments, stack.zy, stack.first_weight.weight, stack.n_rows)
            if solved.ok and solved.obj < best:
                best, best_gamma = solved.obj, float(gamma)
        if math.isfinite(best_gamma):
            extra.append(best_gamma)
    return np.unique(np.concatenate([grid, np.asarray(extra)]))


def candidate_moments(
    replay: Replay, support: FloatArray, candidates: FloatArray, min_regime: int
) -> list[FloatArray | None]:
    """Return ``Z'X(gamma)/n`` of the candidates, reusing search entries of an equal model.

    In the jump model two thresholds with the same split of the observed values of ``q`` give
    bit-for-bit the same regressors, hence the same moments as the initial-grid entry with that
    split; reusing it keeps the statistic of the estimate exactly zero, as in Stata.  In the kink
    model only the same threshold qualifies.  The other candidates are computed in one pass.
    """
    # Stata: xdpt2_build_gamma_cache_t recomputes dW per gamma, so equal splits are bit-equal
    stack, search = replay.stack, replay.search
    initial = search.cache.gammas[: search.n_stage1]
    if stack.kink:
        key_of = {float(g): i for i, g in reversed(list(enumerate(initial)))}
        keys = [key_of.get(float(c), -1) for c in candidates]
    else:
        values = np.unique(stack.level_q[stack.level_support])
        values = values[np.isfinite(values)]
        first: dict[int, int] = {}
        for i, g in reversed(list(enumerate(initial))):
            first[int(np.searchsorted(values, g, side="right"))] = i
        keys = [first.get(int(np.searchsorted(values, c, side="right")), -1) for c in candidates]
    out: list[FloatArray | None] = [None] * candidates.size
    fresh = [i for i, key in enumerate(keys) if key < 0]
    for i, key in enumerate(keys):
        if key >= 0:
            out[i] = search.cache.zw[key]
    if fresh:
        cache = ThresholdCache(stack, support, min_regime)
        cache.add(candidates[fresh])
        order = {float(g): m for g, m in zip(cache.gammas, cache.zw, strict=True)}
        for i in fresh:
            out[i] = order[float(candidates[i])]
    return out


def _distance(objective: float, floor: float) -> float:
    """``J - min(J, floor)``, exactly zero when the two agree to rounding.

    A candidate with the same regime split as the minimiser has the very same criterion in Stata
    (bit for bit); the arrays here may be summed in another order, so a gap of ``1e-12`` of the
    criterion is zero.
    """
    gap = objective - min(objective, floor)
    return 0.0 if gap <= objtol(objective, floor, 1e-12) else gap


class _Inversion:
    """Candidate-by-candidate inversion of the wild grid-bootstrap test."""

    def __init__(
        self, replay: Replay, support: FloatArray, candidates: FloatArray,
        streams: BootstrapStreams, n_boot: int, min_regime: int, component: str,
        exact: bool = False, center: bool = True,
    ) -> None:  # fmt: skip
        stack, search = replay.stack, replay.search
        self.replay, self.stack, self.candidates = replay, stack, candidates
        self.streams, self.n_boot, self.component = streams, n_boot, component
        self.center = center
        self.n = stack.n_rows
        self.moments = candidate_moments(replay, support, candidates, min_regime)
        self.family = make_family(self.moments, replay.weight, replay.n_params)
        self.unrestricted = replay.family
        self.solvable = np.flatnonzero(replay.family.solvable)
        stage2 = search.stage2_global_obj
        self.reference = stage2 if replay.twostep and np.isfinite(stage2) else search.fit.obj
        self.sample_grid: FloatArray | None = None
        if not replay.twostep:
            self.sample_grid = criterion(self.unrestricted, stack.zy[:, None], self.n)[:, 0]
        self.weights: FloatArray | None = None
        self.exact = exact
        self.resampler: UnitResampler | None = None

    def sample(self, index: int) -> tuple[FloatArray, float, float] | int:
        """``(theta, J, D)`` of candidate ``index`` on the sample, or the status of its failure."""
        stack, moments, n = self.stack, self.moments[index], self.n
        assert moments is not None
        if self.replay.twostep:
            solved = solve_fixed_weight(moments, stack.zy, self.replay.weight, n)
            if not solved.ok:
                return SAMPLE_FAILED if self.family.solvable[index] else NOT_ADMISSIBLE
            return solved.theta, solved.obj, _distance(solved.obj, self.reference)
        if not self.family.solvable[index]:
            return NOT_ADMISSIBLE
        theta = self.family.solver[index] @ stack.zy
        objective = float(criterion(self.family, stack.zy[:, None], n, np.array([index]))[0, 0])
        if not math.isfinite(objective):
            return SAMPLE_FAILED
        assert self.sample_grid is not None
        found = self.sample_grid[np.isfinite(self.sample_grid)]
        floor = min(objective, float(np.min(found))) if found.size else objective
        return theta, objective, _distance(objective, floor)

    def unit_distances(self, index: int, theta: FloatArray) -> FloatArray:
        """Return the unit-resampling distances (every candidate draws its own resamples)."""
        if self.resampler is None:
            initial = self.replay.search.cache
            self.resampler = UnitResampler(
                self.stack,
                initial.gammas[: self.replay.search.n_stage1],
                initial.zw[: self.replay.search.n_stage1],
                self.stack.first_weight.weight,
                self.replay.search.fit.gamma,
                self.replay.search.fit.theta,
                self.center,
            )
        return self.resampler.distances(
            self.streams, self.component, float(self.candidates[index]), theta,
            self.replay.weight, self.n_boot,
        )  # fmt: skip

    def distances(self, index: int, theta: FloatArray) -> FloatArray:
        """Bootstrap distances of candidate ``index`` (``nan`` where a draw is invalid)."""
        stack, n = self.stack, self.n
        if self.exact:
            return self.unit_distances(index, theta)
        batch = bool(self.family.solvable[index]) and self.solvable.size > 0
        if not (batch or not self.replay.twostep):
            return np.full(self.n_boot, np.nan)
        if self.weights is None:
            self.weights = mammen_weights(
                self.streams.stream(self.component), stack.n_units, self.n_boot
            )
        if not batch:
            return np.full(self.n_boot, np.nan)
        fitted = stack.regressors(float(self.candidates[index])) @ theta
        draws = sample_moments(
            stack.z.rmatmul(fitted) / n,
            contributing_moments(stack, stack.dy - fitted),
            self.weights,
            n,
        )
        restricted = criterion(self.family, draws, n, np.array([index]))[0]
        alternative = _alternative_minimum(criterion(self.unrestricted, draws, n, self.solvable))
        return _distances(restricted, alternative)


def confidence_set(
    replay: Replay, support: FloatArray, candidates: FloatArray, streams: BootstrapStreams, *,
    n_boot: int, alpha: float, min_regime: int, component: str = "threshold",
    exact: bool = False, center: bool = True,
) -> tuple[ConfidenceSet, FloatArray | None]:  # fmt: skip
    """Invert the wild grid-bootstrap test over ``candidates``.

    Returns
    -------
    ConfidenceSet
        Table, segments and hull.
    numpy.ndarray or None
        Bootstrap distances of the last evaluated candidate (for the p-value of ``citest``).
    """
    # Stata: xdpt2_grid_bootstrap (xtdpthresh.ado:6697), wild path
    inversion = _Inversion(
        replay, support, candidates, streams, n_boot, min_regime, component, exact, center
    )
    table = np.full((candidates.size, 6), np.nan)
    table[:, 0] = candidates
    last: FloatArray | None = None
    valid_counts: list[int] = []
    with Progress(f"confidence set ({component})", candidates.size) as progress:
        for index in range(candidates.size):
            progress.step()
            if inversion.moments[index] is None:
                table[index, 5] = NOT_ADMISSIBLE
                continue
            outcome = inversion.sample(index)
            if isinstance(outcome, int):
                table[index, 5] = outcome
                continue
            theta, _, distance = outcome
            if distance == 0:
                table[index, [1, 3, 5]] = (distance, 1, MECHANICAL)
                continue
            distances = inversion.distances(index, theta)
            n_valid = int(np.isfinite(distances).sum())
            valid_counts.append(n_valid)
            crit = critical_value(distances, 1.0 - alpha) if n_valid == n_boot else math.nan
            if n_valid < n_boot or math.isnan(crit):
                table[index, 4:6] = (n_valid, FEW_DRAWS if n_valid < n_boot else NO_QUANTILE)
                continue
            table[index, 1:6] = (
                distance, crit if math.isfinite(crit) else math.nan, distance <= crit, n_valid,
                VALID,
            )  # fmt: skip
            last = distances
    return _summarise(table, candidates, valid_counts), last


def _summarise(table: FloatArray, candidates: FloatArray, valid_counts: list[int]) -> ConfidenceSet:
    """Hull, runs and counters of the inversion table."""
    # Stata: end of xdpt2_grid_bootstrap (xtdpthresh.ado:7354-7425)
    status = table[:, 5]
    accepted = table[:, 3] == 1
    passed = ~np.isin(status, (NOT_ADMISSIBLE, SAMPLE_FAILED)) & ~np.isnan(status)
    admitted = np.flatnonzero(passed)
    grid_lo = float(candidates[admitted[0]]) if admitted.size else math.nan
    grid_hi = float(candidates[admitted[-1]]) if admitted.size else math.nan
    where = np.flatnonzero(accepted)
    lo = float(candidates[where[0]]) if where.size else math.nan
    hi = float(candidates[where[-1]]) if where.size else math.nan
    starts = np.flatnonzero(accepted & ~np.r_[False, accepted[:-1]])
    stops = np.flatnonzero(accepted & ~np.r_[accepted[1:], False])
    segments = np.column_stack([candidates[starts], candidates[stops]]) if starts.size else (
        np.empty((0, 2))
    )  # fmt: skip
    unresolved = int(np.isin(status, (SAMPLE_FAILED, FEW_DRAWS, NO_QUANTILE)).sum())
    empty, n_seg = float(where.size == 0), float(starts.size)
    if unresolved > 0:
        lo = hi = empty = n_seg = math.nan
    return ConfidenceSet(
        table, segments, lo, hi, empty, n_seg, int(admitted.size), grid_lo, grid_hi,
        int(np.isin(status, (VALID, MECHANICAL)).sum()), unresolved,
        float(min(valid_counts)) if valid_counts else math.nan,
    )  # fmt: skip


# --------------------------------------------------------------------------- coefficients
@dataclass(frozen=True)
class CoefficientBootstrap:
    """Threshold-search-aware percentile intervals of the coefficients (``coef_boot``).

    Each draw rebuilds ``y* = W(gamma_hat) theta_hat + resid * eta``, searches the threshold again
    over the estimation grid and re-estimates ``theta`` there (a wild-residual approximation,
    not the Gong-Seo coefficient bootstrap).

    Attributes
    ----------
    interval
        ``(2, k)`` lower and upper bounds (``e(b_bootci)``); ``None`` when not delivered.
    n_valid, n_twostep, n_failed, n_attempted
        Valid draws, those that completed both steps, failed draws and attempted draws.
    n_stage1, n_stage2
        Candidates of the first and second searches of a draw.
    n_skipped
        Candidates left out of the first search (first-step weight not solvable).
    """

    interval: FloatArray | None
    n_valid: int
    n_twostep: int
    n_failed: int
    n_attempted: int
    n_stage1: int
    n_stage2: int
    n_skipped: int


def _second_stage(
    stack: Stack, zws: FloatArray, gammas: FloatArray, zy: FloatArray, resid: FloatArray,
    center: bool,
) -> FloatArray | None:  # fmt: skip
    """Second-step estimate of one bootstrap sample: new weight, new threshold search."""
    # Stata: stage 2 of xdpt2_coef_bootstrap (xtdpthresh.ado:6533-6585)
    n = stack.n_rows
    inverse = syminv(omega_of(stack, resid, center=center))
    if not inverse.ok:
        return None
    w2 = inverse.inv
    w_zw = np.matmul(w2, zws)
    ok, normal_inv = syminv_batch(np.matmul(zws.transpose(0, 2, 1), w_zw))
    theta = np.einsum("gpq,gq->gp", normal_inv, np.einsum("glp,l->gp", w_zw, zy))
    residual = zy[None, :] - np.einsum("glp,gp->gl", zws, theta)
    objective = n * np.einsum("gl,gl->g", residual, residual @ w2)
    objective[~(ok & np.isfinite(theta).all(axis=1))] = np.nan
    pick, count, high = profile_min(objective, gammas)
    if pick < 0 or is_degenerate(float(objective[pick]), high, count):
        return None
    return np.asarray(theta[pick])


def coefficient_bootstrap(
    replay: Replay, streams: BootstrapStreams, n_boot: int, alpha: float, *, twostep: bool,
    symmetric: bool, center: bool,
) -> CoefficientBootstrap:  # fmt: skip
    """Bootstrap intervals of the coefficients with a new threshold search in every draw."""
    # Stata: xdpt2_coef_bootstrap (xtdpthresh.ado:6357)
    stack, search, n = replay.stack, replay.search, replay.stack.n_rows
    fit, cache = search.fit, search.cache
    n1 = search.n_stage1
    none = CoefficientBootstrap(None, 0, 0, 0, 0, 0, 0, 0)
    hit = np.flatnonzero(cache.gammas == fit.gamma)  # also a point added by refine
    if hit.size == 0 or cache.zw[int(hit[0])] is None:
        return none
    w1 = stack.first_weight.weight
    family = make_family(cache.zw, w1, replay.n_params)
    available = [i for i, moments in enumerate(cache.zw) if moments is not None]
    searched = [i for i in available if i < n1 and family.solvable[i]]
    skipped = sum(1 for i in available if not family.solvable[i])
    if not searched:
        return none
    gammas = cache.gammas
    fitted = stack.regressors(fit.gamma) @ fit.theta
    resid = stack.dy - fitted
    weights = mammen_weights(streams.stream("coefficient"), stack.n_units, n_boot)
    moments = sample_moments(
        stack.z.rmatmul(fitted) / n, contributing_moments(stack, resid), weights, n
    )
    objectives = criterion(family, moments, n, np.array(searched))
    do_two = twostep and fit.twostep
    k = fit.theta.size
    draws = np.full((k, n_boot), np.nan)
    row_unit = (np.cumsum(np.diff(stack.unit_ptr) > 0) - 1)[stack.unit]
    zws = family.zw[available]
    regressors: dict[float, FloatArray] = {}
    valid = failed = both = 0
    for b in range(n_boot):
        pick, count, high = profile_min(objectives[:, b], gammas[searched])
        if pick < 0 or is_degenerate(float(objectives[pick, b]), high, count):
            failed += 1
            continue
        chosen = searched[pick]
        zy = moments[:, b]
        if not do_two:
            draws[:, valid] = family.solver[chosen] @ zy
            valid += 1
            continue
        gamma = float(gammas[chosen])
        if gamma not in regressors:
            regressors[gamma] = stack.regressors(gamma)
        y_star = fitted + resid * weights[row_unit, b]
        r1 = y_star - regressors[gamma] @ (family.solver[chosen] @ zy)
        theta2 = _second_stage(stack, zws, gammas[available], zy, r1, center)
        if theta2 is None:
            failed += 1
            continue
        draws[:, valid] = theta2
        valid += 1
        both += 1
    stats = (valid, both, failed, n_boot, len(searched), len(available), skipped)
    if valid < 10 or valid < math.ceil(0.9 * n_boot):
        return CoefficientBootstrap(None, *stats)
    interval = np.empty((2, k))
    for j in range(k):
        column = draws[j, :valid]
        if symmetric:
            spread = float(quantile_type7(np.abs(column - fit.theta[j]), 1.0 - alpha))
            interval[:, j] = (fit.theta[j] - spread, fit.theta[j] + spread)
        else:
            interval[:, j] = quantile_type7(column, np.array([alpha / 2.0, 1.0 - alpha / 2.0]))
    if not np.all(np.isfinite(interval)):
        return CoefficientBootstrap(None, *stats)
    return CoefficientBootstrap(interval, *stats)


# ---------------------------------------------------------------------------------- citest
@dataclass(frozen=True)
class GammaTest:
    """Grid-bootstrap test of ``H0: gamma = #`` (``citest``).

    Attributes
    ----------
    gamma, statistic, crit
        Hypothesised threshold, distance ``D`` and critical value.
    accepted, n_valid, status
        Decision, valid draws and status of the inversion row.
    p_value
        ``(1 + #{D* >= D}) / (1 + B)``; its ``p > alpha`` is exactly ``D <= crit``.
    """

    gamma: float
    statistic: float
    crit: float
    accepted: float
    n_valid: float
    status: float
    p_value: float


def gamma_test(
    replay: Replay, support: FloatArray, gamma: float, streams: BootstrapStreams, *,
    n_boot: int, alpha: float, min_regime: int, exact: bool = False, center: bool = True,
) -> GammaTest:  # fmt: skip
    """Test ``gamma = #`` with the statistic, bootstrap and weight of the confidence set."""
    # Stata: citest (xtdpthresh.ado:9272-9304)
    ci, distances = confidence_set(
        replay, support, np.array([gamma], dtype=np.float64), streams, n_boot=n_boot,
        alpha=alpha, min_regime=min_regime, component="citest", exact=exact, center=center,
    )  # fmt: skip
    row = ci.table[0]
    p_value = math.nan
    if row[5] == MECHANICAL:
        p_value = 1.0
    elif row[5] == VALID and distances is not None and distances.size:
        finite = distances[np.isfinite(distances)]
        p_value = (1 + int(np.sum(finite >= row[1]))) / (1 + finite.size)
    return GammaTest(
        float(row[0]),
        float(row[1]),
        float(row[2]),
        float(row[3]),
        float(row[4]),
        float(row[5]),
        p_value,
    )


# --------------------------------------------------------------------------------- driver
@dataclass(frozen=True)
class BootstrapResults:
    """Everything the bootstraps of one fit produce.

    Attributes
    ----------
    ci
        Confidence set of the threshold (``None`` when it was not requested).
    linearity
        Linearity test (``None`` with ``linearity_test=False``).
    seed
        ``rseed`` (``None`` when the streams were not seeded).
    """

    ci: ConfidenceSet | None
    linearity: LinearityTest | None
    seed: int | None
    continuity: ContinuityTest | None = None
    citest: GammaTest | None = None
    coefficient: CoefficientBootstrap | None = None


def run_bootstrap(
    stack: Stack,
    search: SearchResult,
    support: FloatArray,
    *,
    trim: float,
    grid_ci: int,
    grid_type: GridType,
    n_boot: int,
    level: float,
    seed: int | None,
    linearity: bool,
    continuity: bool = False,
    citest: float | None = None,
    coef_boot: str = "none",
    coef_symmetric: bool = True,
    center: bool = True,
    boot_type: str = "wild",
) -> BootstrapResults:
    """Run the bootstraps in the order of the command: confidence set, then linearity."""
    # Stata: xtdpthresh_run, "Grid bootstrap CI + linearity test" (xtdpthresh.ado:9078-9250)
    replay = make_replay(stack, search)
    exact = boot_type == "unit"
    if exact and not search.fit.twostep:
        raise DataError(message("xd_unit_one_step"), stata_code=498, key="xd_unit_one_step")
    streams = BootstrapStreams(seed)
    candidates = confidence_grid(
        replay, support, trim=trim, n_grid=grid_ci, grid_type=grid_type,
        min_regime=search.min_regime, exact=exact,
    )  # fmt: skip
    ci, _ = confidence_set(
        replay, support, candidates, streams, n_boot=n_boot, alpha=1.0 - level / 100.0,
        min_regime=search.min_regime, exact=exact, center=center,
    )  # fmt: skip
    alpha = 1.0 - level / 100.0
    test = linearity_test(replay, streams, n_boot) if linearity else None
    jump_vs_kink = None
    if continuity and linearity and not stack.kink:
        jump_vs_kink = continuity_test(replay, support, streams, n_boot, search.min_regime)
    coefficient = None
    if coef_boot != "none":
        coefficient = coefficient_bootstrap(
            replay, streams, n_boot, alpha, twostep=coef_boot == "twostep",
            symmetric=coef_symmetric, center=center,
        )  # fmt: skip
    check = None
    if citest is not None:
        check = gamma_test(
            replay, support, citest, streams, n_boot=n_boot, alpha=alpha,
            min_regime=search.min_regime, exact=exact, center=center,
        )  # fmt: skip
    return BootstrapResults(ci, test, seed, jump_vs_kink, check, coefficient)
