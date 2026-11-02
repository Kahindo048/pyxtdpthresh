"""data layer against the frozen Stata 17 results (xtset balance, L., L2., markout)."""

import json

import numpy as np
import pytest
from validation import compare
from validation.data_cases import GOLDEN, SCENARIOS, python_results, scenario_frame

from pyxtdpthresh._errors import DataError
from pyxtdpthresh.data.checks import require_strongly_balanced
from pyxtdpthresh.data.panel import build_panel

pytestmark = pytest.mark.golden
MASTER = json.loads(GOLDEN.read_text(encoding="utf-8"))


@pytest.mark.parametrize("scenario", SCENARIOS)
def test_scenario_against_stata(scenario):
    py = python_results(scenario)
    for kind, expected in MASTER["stata"][scenario].items():
        diff = compare.compare_arrays(
            kind, py[kind], np.array(expected, dtype=float), atol=1e-12, rtol=1e-12
        )
        assert diff.ok, f"{scenario}: {diff.line()}"


def test_three_balance_classes_are_covered():
    codes = {MASTER["stata"][s]["balance"][0][0] for s in SCENARIOS}
    assert codes == {1.0, 2.0, 3.0}


def test_xthenreg_requirement_accepts_only_the_strongly_balanced_panel():
    for scenario in SCENARIOS:
        panel = build_panel(scenario_frame(scenario), ["invest"], id="firm", time="year")
        if scenario == "full":
            require_strongly_balanced(panel.unit_of_row, panel.time)
        else:
            with pytest.raises(DataError):
                require_strongly_balanced(panel.unit_of_row, panel.time)
