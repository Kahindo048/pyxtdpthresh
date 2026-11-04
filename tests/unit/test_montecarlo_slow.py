"""Statistical consistency of the estimator on simulated panels (H.8.4, via I.5).

Small experiments, so that the suite stays fast enough: the bounds are several Monte Carlo
standard errors away from the values of the paper, not a replication of its tables (the report of
``tools/monte_carlo_gong_seo.py`` is).
"""

import pytest

from pyxtdpthresh.extras.simulation import monte_carlo

pytestmark = pytest.mark.slow

OPTIONS = {"n_boot": 99, "grid": 50, "grid_ci": 50}


@pytest.fixture(scope="module")
def discontinuous():
    """Table 1 of Gong and Seo at jump = 1: the paper's Grid-B covers 96.6 % at n = 400."""
    return monte_carlo(
        "gong_seo", 400, 6, reps=60, seed=2026, workers=4, simulation={"jump": 1.0}, **OPTIONS
    )


def test_every_replication_is_estimated(discontinuous):
    assert discontinuous.n_failed == 0
    assert (discontinuous.ok["n_units"] == 400).all()


def test_the_confidence_set_covers_the_true_threshold(discontinuous):
    """The hull of the accepted set covers at least 88 % of the time (nominal 95 %).

    With 60 replications and a true coverage of 95 %, falling to 88 % or less has a probability
    of about 4 %; at the 99 % the paper finds it is negligible.
    """
    share, error, count = (
        discontinuous.threshold_coverage().loc["hull", ["coverage", "mcse", "n"]].tolist()
    )
    assert count == 60 and share >= 0.88, (share, error)


def test_the_threshold_is_estimated_close_to_the_truth_on_average(discontinuous):
    gamma = discontinuous.estimates().loc["gamma"]
    assert abs(gamma["median_bias"]) < 0.3
    assert gamma["rmse"] < 0.8  # q has a standard deviation of 1.4


def test_the_linearity_test_rejects_a_strong_threshold_effect(discontinuous):
    assert discontinuous.linearity()["kind"] == "power"
    assert discontinuous.linearity()["rate"] > 0.95


def test_the_linearity_test_has_the_right_size_without_a_threshold():
    """Under a linear model the 5 % test rejects about 5 % of the time (at most 15 % here)."""
    out = monte_carlo("linear", 400, 6, reps=60, seed=7, workers=4, **OPTIONS)
    lin = out.linearity()
    assert lin["kind"] == "size" and out.n_failed == 0
    assert lin["rate"] <= 0.15, lin


def test_the_slopes_are_covered_by_their_asymptotic_intervals(discontinuous):
    estimates = discontinuous.estimates()
    assert estimates.loc["upper:L.y", "coverage"] >= 0.8
    assert estimates["coverage"].mean() >= 0.85
