"""core.linalg against the frozen Stata 17 results (Mata invsym/cholinv, xdpt2_* verbatim)."""

import json

import numpy as np
import pytest
from validation import compare
from validation.linalg_cases import GOLDEN, python_results

from pyxtdpthresh.core import linalg

pytestmark = pytest.mark.golden
MASTER = json.loads(GOLDEN.read_text(encoding="utf-8"))
NAMES = list(MASTER["matrices"])


@pytest.mark.parametrize("name", NAMES)
def test_matrix_against_stata(name):
    a = np.array(MASTER["matrices"][name], dtype=float)
    py = python_results(name, a)
    rtol = MASTER["rtol_override"].get(name, compare.RTOL)
    for kind, expected in MASTER["stata"][name].items():
        diff = compare.compare_arrays(kind, py[kind], np.array(expected, dtype=float), rtol=rtol)
        assert diff.ok, f"{name}: {diff.line()}"


def test_objtol_against_stata():
    for args, expected in zip(MASTER["objtol_args"], MASTER["objtol"], strict=True):
        assert linalg.objtol(*args) == pytest.approx(expected, rel=1e-12, abs=0.0)


def test_admission_decisions_cover_both_outcomes():
    flags = [MASTER["stata"][n]["syminv_ok"][0][0] for n in NAMES]
    assert 0.0 in flags and 1.0 in flags
