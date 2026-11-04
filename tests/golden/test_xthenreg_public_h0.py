"""The public ``xthenreg(..., h_0=)`` gives the covariance of Stata's ``xthenreg ..., h_0()``.

c7 uses ``h_0(3)`` and c8 ``h_0(0.7)`` (the default is 1.5); the frozen Stata results are compared
through the public function, with the same data, sample and options as the Stata run.
"""

import json

import numpy as np
import pytest
from validation import compare
from validation.cases import XTHENREG_CASES, load_invest
from validation.freeze import GOLDEN

from pyxtdpthresh import xthenreg

pytestmark = pytest.mark.golden
MASTER = json.loads(GOLDEN.read_text(encoding="utf-8"))["cases"]
H0_CASES = [c for c in XTHENREG_CASES if c.h_0 is not None]


@pytest.mark.parametrize("case", H0_CASES, ids=lambda c: c.tag)
def test_covariance_with_another_bandwidth_multiplier_matches_stata(case):
    res = xthenreg(
        load_invest(max_year=case.max_year), case.y, list(case.x), q=case.q,
        endogenous=list(case.endogenous), exogenous=list(case.exogenous), inst=list(case.inst),
        id="firm", time="year", static=case.static, kink=case.kink,
        grid_num=case.grid_num, trim_rate=case.trim_rate, h_0=case.h_0,
    )  # fmt: skip
    expected = MASTER[case.tag]
    for name, got in (("b", res.fit.coef), ("V", res.cov.to_numpy()), ("CI", res.ci.to_numpy())):
        diff = compare.compare_arrays(name, got, np.array(expected[name], dtype=float))
        assert diff.ok, f"{case.tag}: {diff.line()}"
    assert len(H0_CASES) == 2
