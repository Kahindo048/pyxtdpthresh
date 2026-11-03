"""``xtdpthresh`` and ``xthenreg`` agree on the same grid when their designs coincide (E.6).

Both Stata programs estimate the same model in first differences with Arellano-Bond instruments
and the same two-step weights.  Given the same candidate thresholds, the Python ports must give
the same threshold and coefficients wherever the designs are identical: all-endogenous
regressors (c1), regressors with external instruments (c4) and the static kink model (c5).  The
kink model with a refined threshold (c2) differs only by the off-grid refinement that
``xtdpthresh`` adds.  Cases with an exogenous variable equal to the threshold variable (c3, c6) are
excluded: the two Stata programs build different instrument sets there (``xthenreg`` reports 87
moment conditions where ``xtdpthresh`` has 60 instruments for the same data).
"""

import warnings

import numpy as np
import pytest
from validation.cases import XTHENREG_CASES, load_invest
from validation.runner import estimate_case

from pyxtdpthresh._errors import PyxdpthreshWarning
from pyxtdpthresh.models.xtdpthresh.fit import fit_point

BY_TAG = {c.tag: c for c in XTHENREG_CASES}


def both(tag):
    case = BY_TAG[tag]
    reference = estimate_case(case)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", PyxdpthreshWarning)
        fit = fit_point(
            load_invest(max_year=case.max_year),
            case.y,
            list(case.x),
            q=case.q,
            id="firm",
            time="year",
            endogenous=case.endogenous,
            exogenous=case.exogenous,
            iv=case.inst,
            kink=case.kink,
            static=case.static,
            grid=case.grid_num,
            trim=case.trim_rate,
            bootstrap=False,
            grid_values=reference.grid,
        )
    return reference, fit.search


@pytest.mark.parametrize("tag", ["c1", "c4", "c5"])
def test_same_grid_same_threshold_and_coefficients(tag):
    reference, result = both(tag)
    assert result.fit.gamma == pytest.approx(reference.gamma, abs=5e-5)
    coefficients = np.ravel(reference.coef)[: result.fit.theta.size]
    np.testing.assert_allclose(result.fit.theta, coefficients, atol=5e-5, rtol=1e-6)


def test_kink_differs_only_by_the_refinement_off_the_grid():
    reference, result = both("c2")
    assert result.kink_refined
    assert result.fit.gamma == pytest.approx(reference.gamma, abs=0.01)
    coefficients = np.ravel(reference.coef)[: result.fit.theta.size]
    np.testing.assert_allclose(result.fit.theta, coefficients, atol=0.01)
