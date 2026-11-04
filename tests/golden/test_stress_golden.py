"""Random panels and random option combinations against Stata 17 (stress test, K.5).

120 scenarios drawn by ``validation.stress`` (size, unbalance, missing values, shape of the
threshold variable, roles of the regressors, method, kink, time effects, collapse, lags,
bootstrap) were run in Stata.  A scenario Stata refuses must be refused with the same return code;
one Stata estimates must agree on every object of the result.  Two scenarios are degenerate (more
instruments than equations, a flat criterion) and are decided by rounding noise: they are
expected to differ, and the test says so if they ever agree.
"""

import pytest
from validation import stress, stress_cases

pytestmark = pytest.mark.golden

GOLDEN = stress_cases.frozen()
SCENARIOS = {s.name: s for s in stress.scenarios(GOLDEN["meta"]["count"], GOLDEN["meta"]["seed"])}
#: Scenarios on which Stata and the package differ because the answer is rounding noise.
NOISE = {
    "s009": "kink, 25 units for 34 instruments: the criterion is flat (exactly zero) over part of "
    "the grid and the extra candidate of the confidence set is the first of the tied minima",
    "s047": "50 equations for 80 instrument columns once the time effects are partialled out: the "
    "42nd pivot of the dependence rule is rounding noise (1.1e-13 against the limit 1e-13)",
}


def check(name):
    s, ref = SCENARIOS[name], GOLDEN["cases"][name]
    if stress_cases.digest(stress_cases.frame_of(s)) != ref["digest"]:
        pytest.skip(
            "the random generator of NumPy has changed: refreeze with validation.stress_cases"
        )
    kind, detail = stress_cases.verdict(s, ref)
    if kind == "ok":
        bad = [r for r in detail if not r.ok]
        if bad:
            return "DIFFERENT", [(r.name, r.python, r.stata) for r in bad[:4]]
    return kind, detail


@pytest.mark.parametrize("name", [n for n in SCENARIOS if n not in NOISE])
def test_the_scenario_agrees_with_stata(name):
    kind, detail = check(name)
    assert kind in ("ok", "both refuse"), detail


@pytest.mark.parametrize("name", list(NOISE))
def test_the_degenerate_scenarios_are_still_decided_by_noise(name):
    kind, _ = check(name)
    assert kind == "DIFFERENT", f"{name} now agrees with Stata: {NOISE[name]}"


def test_the_scenarios_cover_both_outcomes_and_every_kind_of_threshold_variable():
    refused = [n for n, c in GOLDEN["cases"].items() if c["rc"] != 0]
    assert 15 <= len(refused) <= 40 and len(refused) < len(SCENARIOS)
    assert {s.q_kind for s in SCENARIOS.values()} == set(stress.Q_KINDS)
    assert {s.options["method"] for s in SCENARIOS.values()} == {"fd", "fod"}
    assert any(s.options["kink"] for s in SCENARIOS.values())
    assert any(s.options["time_effects"] for s in SCENARIOS.values())
