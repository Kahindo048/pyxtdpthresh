"""Run a reference ``xthenreg`` case with the Python package (used by the golden tests)."""

from __future__ import annotations

import warnings

from pyxtdpthresh.core.grids import xthenreg_grid
from pyxtdpthresh.models.xthenreg import estimator
from pyxtdpthresh.models.xthenreg.design import (
    XthenregData,
    build_instruments,
    prepare_data,
)
from pyxtdpthresh.models.xthenreg.estimate import estimate
from pyxtdpthresh.models.xthenreg.moments import Engine, XthenregProblem, make_problem
from pyxtdpthresh.results.containers import XthenregFit
from validation.cases import XthenregCase, load_invest


def case_data(case: XthenregCase) -> XthenregData:
    """Estimation sample of one case."""
    df = load_invest(max_year=case.max_year)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return prepare_data(
            df, case.y, case.q, case.x, case.endogenous, case.exogenous, case.inst,
            id="firm", time="year",
        )  # fmt: skip


def build_case(case: XthenregCase) -> tuple[XthenregProblem, object]:
    """Data, instruments, problem and grid of one case; returns ``(problem, grid)``."""
    data = case_data(case)
    inst = build_instruments(data, static=case.static)
    problem = make_problem(data, inst, static=case.static, kink=case.kink)
    return problem, xthenreg_grid(data.q, case.trim_rate, case.grid_num)


def fit_case(
    case: XthenregCase, engine: Engine = "fast"
) -> tuple[XthenregProblem, estimator.TwoStepFit]:
    """Fit one reference case; returns ``(problem, fit)``."""
    problem, grid = build_case(case)
    return problem, estimator.fit(problem, grid, engine)  # type: ignore[arg-type]


def estimate_case(case: XthenregCase, engine: Engine = "fast") -> XthenregFit:
    """Complete ``xthenreg`` result of one case (bootstrap weights from ``case.seed``)."""
    return estimate(
        case_data(case),
        static=case.static,
        kink=case.kink,
        grid_num=case.grid_num,
        trim_rate=case.trim_rate,
        h_0=1.5 if case.h_0 is None else case.h_0,
        boot_reps=case.boost,
        seed=case.seed,
        engine=engine,
    )
