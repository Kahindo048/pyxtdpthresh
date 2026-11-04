"""The stress harness itself: scenarios are reproducible, checks run, a bug would be caught."""

import contextlib
import io

import matplotlib
import pytest
from validation import stress

matplotlib.use("Agg")


def test_the_scenarios_are_a_function_of_the_seed():
    a, b = stress.scenarios(20, 1), stress.scenarios(20, 1)
    assert a == b and a != stress.scenarios(20, 2)
    assert {s.q_kind for s in stress.scenarios(120, 1)} == set(stress.Q_KINDS)


def test_a_panel_is_reproducible_and_has_the_asked_shape():
    s = stress.Scenario("t", 5, n=30, t=5, n_exog=2, n_endog=1, unbalanced=0.2, missing=0.1)
    a, b = stress.draw_panel(s), stress.draw_panel(s)
    assert a.equals(b)
    assert list(a.columns) == ["id", "t", "y", "q", "x1", "x2", "e1"]
    assert len(a) < 30 * 5 and a["x1"].isna().any()


def test_the_numbers_check_sees_a_threshold_outside_the_range_of_q():
    s = stress.scenarios(12, 20261104)[0]  # estimated without a refusal
    frame = stress.draw_panel(s)
    res = stress.fit(frame, s)
    assert stress.check_numbers(res, frame) == []
    assert any(
        "outside the range" in p
        for p in stress.check_numbers(res, frame.assign(q=frame["q"] + 1e3))
    )


@pytest.mark.slow
def test_a_small_campaign_finds_no_bug():
    with contextlib.redirect_stdout(io.StringIO()):
        outcomes = stress.run_campaign(6, 20261104)
    assert [o for o in outcomes if o.status == "BUG"] == []
    assert any(o.status == "ok" for o in outcomes)
