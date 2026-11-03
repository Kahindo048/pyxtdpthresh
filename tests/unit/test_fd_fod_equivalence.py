"""First differences and forward deviations on a balanced panel: same units, close estimates."""

import numpy as np
from test_search import simulate

from pyxtdpthresh.models.xtdpthresh.fit import fit_point


def run(method):
    return fit_point(
        simulate(), "y", ["x"], q="q", id="id", time="t", method=method, collapse=True, grid=40,
        bootstrap=False, warn=False,
    )  # fmt: skip


def test_balanced_panel_gives_the_same_units_and_close_estimates():
    fd, fod = run("fd"), run("fod")
    assert fd.n_units == fod.n_units == 400
    # the lagged dependent variable removes the first period: both leave one equation per period
    assert fod.n_obs == fd.n_obs
    np.testing.assert_allclose(fod.search.fit.theta, fd.search.fit.theta, atol=0.35)
    assert abs(fod.search.fit.gamma - fd.search.fit.gamma) < 0.15
