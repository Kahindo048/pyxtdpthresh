"""xthenreg data and instruments against the frozen Stata 17 results (verbatim Mata step 1)."""

import json
import warnings

import numpy as np
import pytest
from validation import compare
from validation.design_cases import FINGERPRINTED, GOLDEN, design_cases, fingerprint, python_results

pytestmark = pytest.mark.golden
MASTER = json.loads(GOLDEN.read_text(encoding="utf-8"))
CASES = {c.tag: c for c in design_cases()}


@pytest.mark.parametrize("tag", list(CASES))
def test_design_against_stata(tag):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        py = python_results(CASES[tag])
    for kind, expected in MASTER["stata"][tag].items():
        if kind in FINGERPRINTED:
            got, want = fingerprint(py[kind]), expected
            for part in ("rows", "cols", "bilinear"):
                diff = compare.compare_arrays(
                    f"{kind}.{part}", np.array(got[part]), np.array(want[part]), 1e-12, 1e-12
                )
                assert diff.ok, f"{tag}: {diff.line()}"
        else:
            diff = compare.compare_arrays(
                kind, py[kind], np.array(expected, dtype=float), atol=1e-12, rtol=1e-12
            )
            assert diff.ok, f"{tag}: {diff.line()}"


def test_the_cases_cover_dynamic_static_missing_values_and_an_if_clause():
    scal = {t: MASTER["stata"][t]["scal"] for t in CASES}
    assert any(s[0][0] < s[2][0] for s in scal.values())  # units dropped for missing values
    assert any(CASES[t].static for t in CASES) and any(not CASES[t].static for t in CASES)
    assert any(CASES[t].min_year for t in CASES) and any(CASES[t].inst for t in CASES)
