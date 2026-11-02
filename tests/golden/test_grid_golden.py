"""core.quantiles and core.grids against the frozen Stata 17 results."""

import json

import numpy as np
import pytest
from validation import compare
from validation.grid_cases import CASES, GOLDEN, python_results

pytestmark = pytest.mark.golden
MASTER = json.loads(GOLDEN.read_text(encoding="utf-8"))


@pytest.mark.parametrize("name", list(CASES))
def test_case_against_stata(name):
    py = python_results(name)
    for kind, expected in MASTER["stata"][name].items():
        diff = compare.compare_arrays(
            kind, py[kind], np.array(expected, dtype=float), atol=1e-12, rtol=1e-12
        )
        assert diff.ok, f"{name}: {diff.line()}"


def test_quantile_grid_with_ties_is_shorter_than_requested():
    assert len(MASTER["stata"]["ties10"]["qgrid"]) < 30
