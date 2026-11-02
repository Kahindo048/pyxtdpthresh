"""xthenreg covariance and confidence intervals against the frozen Stata 17 results (c1 to c6)."""

import json

import numpy as np
import pytest
from validation import compare
from validation.cases import XTHENREG_CASES
from validation.freeze import GOLDEN
from validation.runner import fit_case

from pyxtdpthresh.models.xthenreg.covariance import covariance

pytestmark = pytest.mark.golden
CASES = {c.tag: c for c in XTHENREG_CASES}
MASTER = json.loads(GOLDEN.read_text(encoding="utf-8"))["cases"]


@pytest.mark.parametrize("engine", ["fast", "literal"])
@pytest.mark.parametrize("tag", list(CASES))
def test_variance_and_confidence_intervals_against_stata(tag, engine):
    problem, fit = fit_case(CASES[tag], engine)
    result = covariance(problem, fit)
    for name, got in (("V", result.cov), ("CI", result.ci), ("b", fit.estimates)):
        diff = compare.compare_arrays(name, got, np.array(MASTER[tag][name], dtype=float))
        assert diff.ok, f"{tag}/{engine}: {diff.line()}"


@pytest.mark.parametrize("tag", list(CASES))
def test_covariance_is_symmetric_positive_and_se_match_the_diagonal(tag):
    problem, fit = fit_case(CASES[tag], "fast")
    result = covariance(problem, fit)
    np.testing.assert_allclose(result.cov, result.cov.T, rtol=1e-9, atol=1e-14)
    assert np.all(np.diag(result.cov) > 0)
    np.testing.assert_allclose(result.se**2, np.diag(result.cov))
    assert np.isnan(result.bandwidth) == CASES[tag].kink
