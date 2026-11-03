"""Stacked transformed equations of ``xtdpthresh``: dependent variable, regressors, instruments.

The system is first differences or forward orthogonal deviations of the equation rows.  Each
transformed equation is a weighted sum of level observations (triplets), so the regressors at a
threshold are the transform of the level regressors ``[X, 1(q > g), X 1(q > g)]`` (jump) or
``[X, (q - g) 1(q > g)]`` (kink), formed by a sparse product without restacking.  The
instruments, their cleaning, the time-effect partialling and the first-step weight do not depend
on the threshold and are computed once.
"""

from __future__ import annotations

import math
from collections.abc import Callable
from dataclasses import dataclass

import numpy as np
from scipy import sparse

from pyxtdpthresh._errors import DataError
from pyxtdpthresh._i18n import message
from pyxtdpthresh._types import FloatArray, IntArray
from pyxtdpthresh.core.linalg import syminv
from pyxtdpthresh.core.weights import FirstStepWeight, stacked_ma1_weight
from pyxtdpthresh.instruments.builder import (
    EXOGENOUS,
    InstrumentSettings,
    build_instruments,
    observed_periods,
)
from pyxtdpthresh.instruments.cleaning import CleanedInstruments, clean_instruments
from pyxtdpthresh.instruments.matrix import InstrumentMatrix
from pyxtdpthresh.kernels.moments import regime_moments
from pyxtdpthresh.models.xtdpthresh.sample import XtdpthreshData
from pyxtdpthresh.transforms.fd import FDEquations, fd_equations
from pyxtdpthresh.transforms.fod import fod_equations
from pyxtdpthresh.transforms.td import Partialling, fd_time_effects, fod_time_effects

#: Fewest stacked equations the estimator accepts.
MIN_ROWS = 20
#: A column whose sum falls below this share of its sum before the projection is gone.
GONE_TOL = 1e-10


@dataclass(frozen=True)
class Stack:
    """Transformed system of the retained units, rows sorted by (unit, period).

    Attributes
    ----------
    dy, dx
        Transformed dependent variable ``(n,)`` and regressors ``(n, K)`` (after the time-effect
        projection when there is one).
    unit, time
        Unit index (0-based among the retained units) and period of each equation.
    unit_ptr
        Unit ``i`` owns the stacked rows ``unit_ptr[i]:unit_ptr[i + 1]``.
    instruments
        Cleaned instruments and what was removed.
    z
        The cleaned (and, with time effects, projected) instrument matrix.
    first_weight
        First-step weight and the fallback that produced it.
    zy, zdx
        ``Z'dy / n`` and ``Z'dX / n``.
    kink
        Continuous (kink) model: one regime column ``(q - gamma)_+`` instead of the jump terms.
    names
        Name of each column of ``dx``.
    level_x, level_q
        Regressors and threshold variable at the level observations that enter the equations.
    transform, kept_transform
        Sparse triplets of every candidate equation and of the kept equations.
    partial, keep
        Time-effect projection (or None) and the candidate equations that are kept.
    current_level
        Index into ``level_q`` of the level row of each kept equation (the row of period ``t``).
    row
        Row of the prepared data (the period ``t`` observation) of each kept equation.
    q_sd, q_values
        Standard deviation and sorted distinct values of the threshold variable over every level
        observation of the sample (they set and check the kernel bandwidth of the joint variance).
    """

    dy: FloatArray
    dx: FloatArray
    unit: IntArray
    time: IntArray
    unit_ptr: IntArray
    instruments: CleanedInstruments
    z: InstrumentMatrix
    first_weight: FirstStepWeight
    zy: FloatArray
    zdx: FloatArray
    kink: bool
    names: tuple[str, ...]
    level_x: FloatArray
    level_q: FloatArray
    transform: sparse.csr_matrix
    kept_transform: sparse.csr_matrix
    partial: Partialling | None
    keep: IntArray
    current_level: IntArray
    row: IntArray
    q_sd: float
    q_values: FloatArray

    @property
    def n_rows(self) -> int:
        """Number of stacked equations."""
        return int(self.dy.size)

    @property
    def n_instruments(self) -> int:
        """Number of instruments after cleaning."""
        return int(self.z.shape[1])

    @property
    def n_units(self) -> int:
        """Units that have at least one stacked equation."""
        return int(np.count_nonzero(np.diff(self.unit_ptr)))

    @property
    def level_support(self) -> IntArray:
        """Level observations (index into ``level_q``) that enter a kept equation."""
        return np.unique(self.kept_transform.indices)

    def _regime_levels(self, gamma: float) -> FloatArray:
        """Level regressors ``[X, regime terms]`` at threshold ``gamma``."""
        above = (self.level_q > gamma).astype(np.float64)
        if self.kink:
            return np.column_stack([self.level_x, (self.level_q - gamma) * above])
        return np.column_stack([self.level_x, above, self.level_x * above[:, None]])

    def transform_levels(self, values: FloatArray) -> FloatArray:
        """Transform level columns ``(n_levels[, m])`` into the kept, partialled equations."""
        # Stata: xdpt2_tpl_trans (xtdpthresh.ado:4987)
        full = np.asarray(self.transform @ values)
        if self.partial is not None:
            full = self.partial.apply(full)
        return np.asarray(full[self.keep])

    def regressors(self, gamma: float) -> FloatArray:
        """Return the transformed regressors of the kept equations at threshold ``gamma``."""
        # Stata: xdpt2_transform_unit, regime regressors (xtdpthresh.ado:2833-2905)
        return self.transform_levels(self._regime_levels(gamma))

    def bandwidth(self, scale: float) -> float:
        """Kernel bandwidth ``scale * 1.06 * s_q * n^(-1/5)`` of the jump model's joint variance."""
        # Stata: xdpt2_jump_xg_tp (xtdpthresh.ado:5058), n = units with an equation
        return float(scale * 1.06 * self.q_sd * self.n_units ** (-0.2))

    def regime_derivative(self, gamma: float, theta: FloatArray, bandwidth: float) -> FloatArray:
        """Return ``x_g``, the derivative of the transformed residuals in the threshold.

        Jump model: ``-T(phi_h(q - gamma) (1, x') delta)`` with ``phi_h`` the Gaussian kernel and
        ``delta`` the regime-change coefficients (the expected moment is smooth in ``gamma``
        although the sample moment is a step function).  Kink model: ``-delta_k T(1(q > gamma))``.
        """
        # Stata: xdpt2_jump_xg_tp (xtdpthresh.ado:5035), xdpt2_ar_xg (5149)
        if self.kink:
            above = (self.level_q > gamma).astype(np.float64)
            return np.asarray(-theta[-1] * self.transform_levels(above))
        k = self.level_x.shape[1]
        delta = theta[k : 2 * k + 1]
        u = (self.level_q - gamma) / bandwidth
        density = np.exp(-0.5 * u * u) / (math.sqrt(2.0 * math.pi) * bandwidth)
        weight = density * (delta[0] + self.level_x @ delta[1:])
        return np.asarray(-self.transform_levels(weight))

    def n_switch(self, gamma: float) -> int:
        """Units whose regime changes inside one of their transformed equations at ``gamma``."""
        # Stata: xdpt2_n_switch (xtdpthresh.ado:4274)
        t = self.kept_transform
        if t.indices.size == 0:
            return 0
        above = (self.level_q > gamma).astype(np.int8)[t.indices]
        starts = t.indptr[:-1]
        changes = np.maximum.reduceat(above, starts) != np.minimum.reduceat(above, starts)
        return int(np.unique(self.unit[changes]).size)

    def moments(self, gammas: FloatArray) -> FloatArray:
        """``Z'X(gamma) / n`` for each threshold, ``(G, L, p)``, in one pass over the equations."""
        order = np.argsort(gammas, kind="stable")
        grid = np.ascontiguousarray(gammas[order], dtype=np.float64)
        n = self.n_rows
        t = self.kept_transform
        ones = np.ones((self.level_q.size, 1))
        level = np.column_stack([ones, self.level_q if self.kink else self.level_x])
        regime = regime_moments(
            self.z.csc,
            t.indptr.astype(np.int64),
            t.indices.astype(np.int64),
            np.asarray(t.data, dtype=np.float64),
            level,
            self.level_q,
            grid,
        )
        if self.kink:
            regime = (regime[:, :, 1] - grid[:, None] * regime[:, :, 0])[:, :, None]
        out = np.empty((grid.size, self.zdx.shape[0], self.zdx.shape[1] + regime.shape[2]))
        out[:, :, : self.zdx.shape[1]] = self.zdx
        out[:, :, self.zdx.shape[1] :] = regime / n
        result = np.empty_like(out)
        result[order] = out
        return result


def _settings(data: XtdpthreshData) -> InstrumentSettings:
    opts = data.spec.options
    return InstrumentSettings(
        lag_lo=opts.maxlag[0],
        lag_hi=opts.maxlag[1],
        collapse=opts.collapse,
        iv_collapse=opts.iv_collapse,
        static=opts.static,
        method=opts.method,
    )


def _transform_matrix(eqs: FDEquations, n_levels: int) -> sparse.csr_matrix:
    """Sparse ``(n_equations, n_levels)`` matrix of the triplets."""
    return sparse.csr_matrix(
        (eqs.pair_w, eqs.pair_lev, eqs.pair_ptr), shape=(eqs.row.size, n_levels)
    )


def _first_step_weight(
    z: InstrumentMatrix, unit: IntArray, time: IntArray, method: str
) -> FirstStepWeight:
    """MA(1) weight for first differences, ``(Z'Z)^{-1}`` for forward deviations."""
    # Stata: xdpt2_build_W_ma1 (xtdpthresh.ado:3808) and ZZ_inv for FOD (4558)
    n = z.shape[0]
    if method == "fod":
        return FirstStepWeight(syminv(z.gram() / n).inv, 0)
    n_unit_ids = int(np.max(unit)) + 1
    second = z.gram() / n_unit_ids
    consecutive = np.flatnonzero((unit[1:] == unit[:-1]) & (time[1:] - time[:-1] == 1))
    lag_cross = z.cross_rows(consecutive, consecutive + 1) / n_unit_ids
    return stacked_ma1_weight(second, lag_cross)


def _gone_names(names: tuple[str, ...], before: FloatArray, after: FloatArray) -> list[str]:
    """Regressors whose column sum the time-effect projection reduces to rounding noise."""
    # Stata: xdpt_td_gone (xtdpthresh.ado:3752-3758)
    pre = np.sum(np.abs(before), axis=0)
    post = np.sum(np.abs(after), axis=0)
    return [n for n, a, b in zip(names, pre, post, strict=False) if a > 0 and b <= GONE_TOL * a]


def _time_effects(
    data: XtdpthreshData, transform: sparse.csr_matrix, time: IntArray
) -> Partialling:
    """Projection off the transformed period dummies of the stacked equations."""
    if data.spec.options.method == "fd":
        return fd_time_effects(time)
    periods = observed_periods(data.time, data.eq)
    rank = np.clip(np.searchsorted(periods, data.time), 0, max(periods.size - 1, 0))
    return fod_time_effects(transform, rank.astype(np.int64), int(periods.size))


def _partial_hook(
    partial: Partialling,
) -> Callable[[FloatArray], tuple[FloatArray, IntArray]]:
    """Projection of the instruments, with the exact zeroing of the Stata command."""

    def hook(z: FloatArray) -> tuple[FloatArray, IntArray]:
        before = np.sum(np.abs(z), axis=0)
        projected = partial.apply(z)[partial.keep]
        after = np.sum(np.abs(projected), axis=0)
        # a column constant within the period is projected to rounding noise: make it exact zero
        projected[:, (before > 0) & (after < GONE_TOL * before)] = 0.0
        return projected, partial.keep

    return hook


def _level_spread(q: FloatArray) -> float:
    """Sample standard deviation of the observed values of ``q`` (missing when fewer than two)."""
    values = q[np.isfinite(q)]
    return float(np.std(values, ddof=1)) if values.size > 1 else math.nan


def build_stack(data: XtdpthreshData) -> Stack:
    """Stack the transformed equations of ``data`` with their instruments.

    Equations without any instrument are dropped (the period constant alone does not count);
    with ``time_effects`` the period dummies are partialled out; instrument columns that carry no
    information are removed.

    Raises
    ------
    DataError
        Fewer than 20 usable equations, an instrument matrix that is too large or
        ill-conditioned, too few instruments left after the common-variable columns are removed,
        or a regressor that the unit and time effects remove together (return code 498).
    """
    # Stata: xdpt2_stack_at_gamma (xtdpthresh.ado:3452) and the checks of xtdpthresh_run
    opts = data.spec.options
    make = fod_equations if opts.method == "fod" else fd_equations
    eqs = make(data.offsets, data.time, data.eq, data.y, data.q, data.x)
    transform = _transform_matrix(eqs, data.time.size)
    dx_all = np.asarray(transform @ data.x)
    raw = build_instruments(
        offsets=data.offsets,
        time=data.time,
        eq=data.eq,
        y=data.y,
        x=data.x,
        var_type=data.var_type,
        inst=data.instruments,
        eq_row=eqs.row,
        eq_time=eqs.time,
        d_exog=dx_all[:, data.var_type == EXOGENOUS],
        settings=_settings(data),
    )
    available = raw.keep
    transform = transform[available]
    unit, time, dx_pre = eqs.unit[available], eqs.time[available], dx_all[available]
    dy_pre = np.asarray(transform @ data.y)
    if int(available.sum()) < MIN_ROWS:
        raise DataError(
            message("xd_few_rows", n=int(available.sum())), stata_code=498, key="xd_few_rows"
        )

    partial = _time_effects(data, transform, time) if opts.time_effects else None
    cleaned = clean_instruments(raw.z, time, _partial_hook(partial) if partial else None)
    keep = cleaned.rows
    n = int(keep.size)
    if n < MIN_ROWS:
        raise DataError(message("xd_few_rows", n=n), stata_code=498, key="xd_few_rows")
    z = InstrumentMatrix(cleaned.z)
    if not syminv(z.gram() / n).ok:
        raise DataError(message("xd_z_ill"), stata_code=498, key="xd_z_ill")
    dy, dx = dy_pre, dx_pre
    if partial is not None:
        dy, dx = partial.apply(dy_pre), partial.apply(dx_pre)
        gone = _gone_names(data.names, dx_pre, dx[keep])
        if gone:
            raise DataError(
                message("xd_td_gone", names=" ".join(gone), method=opts.method.upper()),
                stata_code=498,
                key="xd_td_gone",
            )
    dy, dx = dy[keep], dx[keep]
    n_params = (data.x.shape[1] + 1) if opts.kink else (2 * data.x.shape[1] + 1)
    if cleaned.n_common > 0 and z.shape[1] < n_params + 1:
        raise DataError(
            message(
                "xd_common_few",
                dropped=cleaned.n_common,
                left=z.shape[1],
                params=n_params,
                need=n_params + 1,
            ),
            stata_code=498,
            key="xd_common_few",
        )

    unit_k, time_k = unit[keep], time[keep]
    counts = np.bincount(unit_k, minlength=data.n_units)
    used = np.unique(transform.indices)
    remap = np.full(data.time.size, -1, dtype=np.int64)
    remap[used] = np.arange(used.size)
    compact = sparse.csr_matrix(
        (transform.data, remap[transform.indices], transform.indptr),
        shape=(transform.shape[0], used.size),
    )
    return Stack(
        dy=dy,
        dx=dx,
        unit=unit_k,
        time=time_k,
        unit_ptr=np.concatenate([[0], np.cumsum(counts)]).astype(np.int64),
        instruments=cleaned,
        z=z,
        first_weight=_first_step_weight(z, unit_k, time_k, opts.method),
        zy=z.rmatmul(dy) / n,
        zdx=z.rmatmul(dx) / n,
        kink=opts.kink,
        names=data.names,
        level_x=data.x[used],
        level_q=data.q[used],
        transform=compact,
        kept_transform=compact[keep],
        partial=partial,
        keep=keep,
        current_level=remap[eqs.row[available][keep]],
        row=eqs.row[available][keep],
        q_sd=_level_spread(data.q),
        q_values=np.unique(data.q[np.isfinite(data.q)]),
    )
