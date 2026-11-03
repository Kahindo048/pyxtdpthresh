"""Estimation sample and first-difference equations against the frozen Stata 17 run (E.2)."""

import json
import warnings

import numpy as np
import pytest
from validation.sample_cases import FRAGMENTS, GOLDEN, frame, sample_cases, unpack

from pyxtdpthresh._errors import DataError, PyxdpthreshWarning
from pyxtdpthresh.models.xtdpthresh.design import check_specification
from pyxtdpthresh.models.xtdpthresh.sample import prepare_data
from pyxtdpthresh.transforms.fd import fd_equations

pytestmark = pytest.mark.golden

FROZEN = json.loads(GOLDEN.read_text(encoding="utf-8"))["cases"]
CASES = {c.name: c for c in sample_cases() if c.name in FROZEN}


def run_python(case):
    """Samples and equations of a case: ``(data, equations, mask of equation rows)``."""
    df = frame(case)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", PyxdpthreshWarning)
        spec = check_specification(**case.full_args())
        data = prepare_data(df, spec, id="firm", time="year", where=case.where)
    eqs = fd_equations(data.offsets, data.time, data.eq, data.y, data.q, data.x)
    in_equations = np.zeros(len(df), dtype=bool)
    in_equations[data.source_row[eqs.row]] = True
    return data, eqs, in_equations


@pytest.mark.parametrize("name", list(CASES))
def test_sample_and_equations_match_stata(name):
    case, stata = CASES[name], FROZEN[name]
    if stata["rc"] != 0:
        assert case.key is not None, f"{name}: Stata refused a sample that should be valid"
        assert FRAGMENTS[case.key] in stata["text"], f"{name}: Stata said {stata['text']!r}"
        with pytest.raises(DataError) as raised:
            run_python(case)
        assert raised.value.key == case.key
        assert raised.value.stata_code == stata["rc"]
        return
    assert case.key is None, f"{name}: Stata accepted a sample that should be refused"
    data, eqs, in_equations = run_python(case)
    assert eqs.n_equations == stata["n"] == stata["n_stack"]
    assert eqs.n_active_units == stata["n_units"]
    np.testing.assert_array_equal(in_equations, unpack(stata["sample"], stata["size"]))
    assert data.n_units >= eqs.n_active_units


def test_every_case_was_frozen():
    assert set(CASES) == {c.name for c in sample_cases()}
