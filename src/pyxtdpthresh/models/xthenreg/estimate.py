"""Complete ``xthenreg`` estimation: grid, two steps, covariance and linearity test.

This is the Python counterpart of ``maincode_0719``: it assembles the pieces of the other
modules of the package into the objects Stata leaves in ``e()``.
"""

from __future__ import annotations

import numpy as np

from pyxtdpthresh._types import FloatArray
from pyxtdpthresh.core.grids import xthenreg_grid
from pyxtdpthresh.inference.bootstrap.rng import StataRNG
from pyxtdpthresh.models.xthenreg import covariance as cov_mod
from pyxtdpthresh.models.xthenreg import estimator, linearity
from pyxtdpthresh.models.xthenreg.design import XthenregData, build_instruments
from pyxtdpthresh.models.xthenreg.moments import Engine, make_problem
from pyxtdpthresh.results.containers import XthenregFit

#: ``e(boots_p)`` when no bootstrap is requested.
NO_BOOTSTRAP = -1.0


def estimate(
    data: XthenregData,
    *,
    static: bool = False,
    kink: bool = False,
    grid_num: int = 100,
    trim_rate: float = 0.4,
    h_0: float = cov_mod.H_0,
    boot_reps: int = 0,
    seed: int | None = None,
    draws: FloatArray | None = None,
    engine: Engine = "fast",
) -> XthenregFit:
    """Estimate the dynamic panel threshold model of Seo, Kim and Kim (2019).

    Parameters
    ----------
    data
        Balanced sample (:func:`~pyxtdpthresh.models.xthenreg.design.prepare_data`).
    static, kink
        Static model (no lag of ``y``); continuous threshold effect (kink) instead of a jump.
    grid_num, trim_rate
        Number of candidate thresholds and total trimmed share of ``q``.
    h_0
        Multiplier of the kernel bandwidth (jump only).
    boot_reps
        Number of bootstrap replications of the linearity test; ``0`` skips the test.
    seed
        Seed of the Stata-compatible generator that supplies the bootstrap weights; drawn at
        random when omitted.
    draws
        Standard normal weights ``(boot_reps, N)`` to use instead of the generator.
    engine
        ``"fast"`` or ``"literal"`` moment computation.
    """
    # Stata: maincode_0719 (xthenreg.ado:326-860)
    problem = make_problem(data, build_instruments(data, static=static), static=static, kink=kink)
    grid = xthenreg_grid(data.q, trim_rate, grid_num)
    fit = estimator.fit(problem, grid, engine)
    result = cov_mod.covariance(problem, fit, h_0)

    sup, boot_sup, boots_p = float("nan"), np.empty(0), NO_BOOTSTRAP
    draws_given = draws is not None
    if boot_reps > 0:
        if draws is None:
            seed = int(np.random.default_rng().integers(0, 2**31)) if seed is None else seed
            draws = StataRNG(seed).normal((boot_reps, problem.n_units))
        elif np.shape(draws)[0] != boot_reps:
            raise ValueError("draws must have one row per bootstrap replication")
        test = linearity.linearity_test(problem, fit, draws)
        sup, boot_sup, boots_p = test.sup_wald, test.boot_sup, test.p_value

    return XthenregFit(
        coef=fit.estimates,
        cov=result.cov,
        ci=result.ci,
        n_units=problem.n_units,
        n_periods=problem.n_periods,
        boots_p=boots_p,
        grid_num=grid_num,
        trim_rate=trim_rate,
        boot_reps=boot_reps,
        gamma=fit.second.gamma,
        grid=fit.grid,
        criterion=fit.second.criterion,
        n_moments=problem.n_moments,
        sup_wald=sup,
        boot_sup=boot_sup,
        bandwidth=result.bandwidth,
        static=static,
        kink=kink,
        names=coefficient_labels(data.names, static=static, kink=kink),
        y_name=data.y_name,
        q_name=data.q_name,
        seed=seed if boot_reps > 0 and draws_given is False else None,
    )


def coefficient_labels(regressors: tuple[str, ...], *, static: bool, kink: bool) -> tuple[str, ...]:
    """Labels of ``e(b)`` of ``xthenreg``: slopes, regime shifts, then the threshold ``r``."""
    # Stata: coef_list (xthenreg.ado:145-300)
    lag = () if static else ("Lag_y",)
    slopes = tuple(f"{name}_b" for name in (*lag, *regressors))
    if kink:
        return (*slopes, "kink_slope", "r")
    shifts = tuple(f"{name}_d" for name in (*lag, *regressors))
    return (*slopes, "cons_d", *shifts, "r")
