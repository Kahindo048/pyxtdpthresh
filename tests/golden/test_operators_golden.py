"""Time-series operators against the frozen Stata 17 results (E.1.2)."""

import json

import numpy as np
import pytest
from validation import compare
from validation.operator_cases import GOLDEN, panel_frame

from pyxtdpthresh.data.operators import diff as difference
from pyxtdpthresh.data.operators import evaluate, lag, lead, parse_term, parse_terms, seasonal
from pyxtdpthresh.data.panel import build_panel

pytestmark = pytest.mark.golden

FROZEN = json.loads(GOLDEN.read_text(encoding="utf-8"))
CANONICAL = FROZEN["canonical"]


@pytest.mark.parametrize("spelling", list(CANONICAL))
def test_canonical_spelling_and_range_expansion_match_stata(spelling):
    stata = CANONICAL[spelling]
    assert stata["rc"] == 0
    got = " ".join(t.name for t in parse_term(spelling))
    assert got == stata["canonical"]


@pytest.fixture(scope="module")
def panel():
    frame = panel_frame()
    got = build_panel(frame, ["cashflow"], id="firm", time="year")
    keys = FROZEN["keys"]
    np.testing.assert_array_equal(got.time, keys["year"])
    np.testing.assert_array_equal(got.unit_labels[got.unit_of_row], keys["firm"])
    return got


@pytest.mark.parametrize("term", FROZEN["terms"])
def test_operated_values_match_stata_on_a_panel_with_gaps(panel, term):
    (parsed,) = parse_term(term)
    want = np.array([np.nan if v is None else v for v in FROZEN["values"][term]])
    diff = compare.compare_arrays(term, evaluate(panel, parsed), want)
    assert diff.ok, diff.line()


def test_gaps_in_the_calendar_give_missing_lags(panel):
    lagged = evaluate(panel, parse_term("L.cashflow")[0])
    assert np.isnan(lagged).sum() > panel.n_units  # more than one start-of-unit row per unit


def test_helpers_build_the_same_terms_as_the_strings():
    assert lag("x", 2) == parse_term("L2.x")[0]
    assert lead("x") == parse_term("F.x")[0]
    assert difference("x", 2) == parse_term("D2.x")[0]
    assert seasonal("x", 12) == parse_term("S12.x")[0]
    assert str(lag("x", 0)) == "x"
    assert parse_terms(["L(1/2).x", lag("z")]) == [lag("x"), lag("x", 2), lag("z")]


def test_a_term_is_its_own_canonical_form():
    for text in ("x", "L.x", "L2D.x", "FD.x", "DS2.x", "S2S3.x"):
        (term,) = parse_term(text)
        assert term.name == text
        assert parse_term(term.name) == [term]
