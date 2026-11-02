"""Two-step estimates of xthenreg against the frozen Stata 17 coefficients (cases c1 to c6)."""

import json

import numpy as np
import pytest
from validation import compare
from validation.cases import XTHENREG_CASES
from validation.freeze import GOLDEN
from validation.runner import fit_case

pytestmark = pytest.mark.golden
CASES = {c.tag: c for c in XTHENREG_CASES}
MASTER = json.loads(GOLDEN.read_text(encoding="utf-8"))["cases"]


@pytest.mark.parametrize("engine", ["fast", "literal"])
@pytest.mark.parametrize("tag", list(CASES))
def test_coefficients_and_threshold_against_stata(tag, engine):
    _, fit = fit_case(CASES[tag], engine)
    expected = np.array(MASTER[tag]["b"], dtype=float).ravel()
    diff = compare.compare_arrays("b", fit.estimates, expected)
    assert diff.ok, f"{tag}/{engine}: {diff.line()}"
    # far tighter than the four decimals required: same algorithm, same arithmetic
    assert diff.max_abs < 1e-8


@pytest.mark.parametrize("tag", list(CASES))
def test_threshold_is_a_grid_point_and_steps_are_consistent(tag):
    _, fit = fit_case(CASES[tag], "fast")
    assert fit.second.gamma in fit.grid and fit.first.gamma in fit.grid
    assert fit.second.criterion[fit.second.index] == fit.second.criterion.min()
    assert fit.estimates.size == fit.a.shape[2] + 1
