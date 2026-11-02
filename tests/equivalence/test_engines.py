"""The fast engine (cumulative sums over the grid) against the literal Mata-style engine."""

import numpy as np
import pandas as pd
import pytest

from pyxtdpthresh.core.grids import xthenreg_grid
from pyxtdpthresh.models.xthenreg import estimator, moments
from pyxtdpthresh.models.xthenreg.design import build_instruments, prepare_data


def simulated(n=60, t=6, seed=0):
    rng = np.random.default_rng(seed)
    firm = np.repeat(np.arange(n), t)
    year = np.tile(np.arange(t), n)
    q = np.round(rng.standard_normal(n * t), 1)  # ties between q and the grid
    x = rng.standard_normal(n * t)
    e = rng.standard_normal(n * t)
    y = np.zeros(n * t)
    eta = np.repeat(rng.standard_normal(n), t)
    for i in range(n):
        for s in range(1, t):
            k = i * t + s
            y[k] = (
                0.4 * y[k - 1]
                + 0.5 * x[k]
                + (q[k] > 0.2) * (0.8 - 0.6 * x[k])
                + eta[k]
                + 0.5 * e[k]
            )
    return pd.DataFrame({"firm": firm, "year": year, "y": y, "q": q, "x": x, "e": e})


@pytest.mark.parametrize("static", [False, True])
@pytest.mark.parametrize("kink", [False, True])
@pytest.mark.parametrize("endogenous", [(), ("e",)])
def test_engines_agree_on_matrices_and_estimates(static, kink, endogenous):
    df = simulated()
    data = prepare_data(df, "y", "q", ["x"], endogenous, id="firm", time="year")
    inst = build_instruments(data, static=static)
    problem = moments.make_problem(data, inst, static=static, kink=kink)
    grid = xthenreg_grid(data.q, 0.3, 25)
    fast = estimator.fit(problem, grid, "fast")
    literal = estimator.fit(problem, grid, "literal")
    np.testing.assert_allclose(fast.a, literal.a, rtol=1e-11, atol=1e-12)
    np.testing.assert_allclose(fast.estimates, literal.estimates, rtol=1e-8, atol=1e-10)
    assert fast.second.index == literal.second.index


def test_unknown_engine_is_rejected():
    df = simulated()
    data = prepare_data(df, "y", "q", ["x"], id="firm", time="year")
    problem = moments.make_problem(data, build_instruments(data))
    with pytest.raises(ValueError, match="engine"):
        moments.moment_matrices(problem, np.array([0.0]), "turbo")  # type: ignore[arg-type]
