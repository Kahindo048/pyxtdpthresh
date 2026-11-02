"""xthenreg linearity test against the frozen Stata 17 results (sup-Wald, bootstrap, p-value)."""

import json

import numpy as np
import pytest
from validation import compare
from validation.linearity_cases import GOLDEN, linearity_cases
from validation.runner import fit_case

from pyxtdpthresh.inference.bootstrap.rng import StataRNG
from pyxtdpthresh.models.xthenreg import linearity

pytestmark = pytest.mark.golden
CASES = {c.tag: c for c in linearity_cases()}
MASTER = json.loads(GOLDEN.read_text(encoding="utf-8"))["stata"]


@pytest.mark.parametrize("tag", list(CASES))
def test_sup_wald_bootstrap_and_p_value_against_stata(tag):
    case = CASES[tag]
    problem, fit = fit_case(case)
    sample = linearity.sup_wald(problem, fit)
    draws = StataRNG(case.seed).normal((case.boost, problem.n_units))
    result = linearity.linearity_test(problem, fit, draws, sample)
    n, t, p_stata, sup_stata = np.array(MASTER[tag]["scal"], dtype=float).ravel()
    assert (problem.n_units, problem.n_periods) == (n, t)
    for name, got, want in (
        ("sup_wald", [sample.sup], [sup_stata]),
        ("boot_sup", result.boot_sup, MASTER[tag]["wald"]),
        ("cov_wald", sample.cov_wald.reshape(-1, sample.length), MASTER[tag]["covwald"]),
    ):
        diff = compare.compare_arrays(name, np.array(got), np.array(want, dtype=float))
        assert diff.ok, f"{tag}: {diff.line()}"
    assert result.p_value == pytest.approx(p_stata, abs=1e-12)


def test_the_cases_include_intermediate_p_values_and_the_kink_quirk():
    p_values = [MASTER[t]["scal"][2][0] for t in CASES]
    assert sum(0 < p < 1 for p in p_values) >= 4 and sum(p == 0 for p in p_values) >= 5
    for case in CASES.values():
        problem, fit = fit_case(case)
        sample = linearity.sup_wald(problem, fit)
        assert sample.length == (2 if case.kink else problem.k + 1)


def test_injected_draws_reproduce_the_same_statistic_as_the_generator():
    case = CASES["p2"]
    problem, fit = fit_case(case)
    sample = linearity.sup_wald(problem, fit)
    draws = StataRNG(case.seed).normal((case.boost, problem.n_units))
    a = linearity.bootstrap_sup(problem, fit, sample, draws)
    b = linearity.bootstrap_sup(problem, fit, sample, draws.copy(), chunk=7)
    np.testing.assert_allclose(a, b, rtol=1e-13)


def test_bad_draw_shape_is_rejected():
    problem, fit = fit_case(CASES["p1"])
    with pytest.raises(ValueError, match="draws"):
        linearity.bootstrap_sup(problem, fit, linearity.sup_wald(problem, fit), np.zeros((3, 5)))
