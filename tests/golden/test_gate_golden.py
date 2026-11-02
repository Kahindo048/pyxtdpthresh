"""Validation gate of ``xthenreg`` (D.5): the full result against the frozen Stata 17 outputs.

``c1`` to ``c6`` come from ``golden_master.json``; the variants (``grid_num``, ``trim_rate``,
kink, T = 15) and the bootstrap p-values of the real command come from ``gate_golden.json``.
"""

import json

import numpy as np
import pytest
from validation import compare
from validation.cases import XTHENREG_CASES
from validation.freeze import GOLDEN as MASTER_PATH
from validation.gate_cases import BOOT, gate_cases
from validation.gate_cases import GOLDEN as GATE_PATH
from validation.runner import case_data, estimate_case

from pyxtdpthresh.inference.bootstrap.rng import StataRNG
from pyxtdpthresh.models.xthenreg.estimate import estimate

pytestmark = pytest.mark.golden

MASTER = json.loads(MASTER_PATH.read_text(encoding="utf-8"))["cases"]
GATE = json.loads(GATE_PATH.read_text(encoding="utf-8"))["cases"] if GATE_PATH.exists() else {}
CASES = {c.tag: c for c in (*XTHENREG_CASES, *gate_cases()) if c.tag in {**MASTER, **GATE}}
FROZEN = {**MASTER, **GATE}


def _check(tag, fit):
    ref = FROZEN[tag]
    n, t, p = np.ravel(ref["scal"])
    pairs = (
        ("b", fit.coef, np.ravel(ref["b"])),
        ("V", fit.cov, np.array(ref["V"])),
        ("CI", fit.ci, np.array(ref["CI"])),
        ("N", np.array([fit.n_units]), np.array([n])),
        ("T", np.array([fit.n_periods]), np.array([t])),
        ("boots_p", np.array([fit.boots_p]), np.array([p])),
    )
    for name, got, want in pairs:
        diff = compare.compare_arrays(name, got, want)
        assert diff.ok, f"{tag}: {diff.line()}"


@pytest.mark.parametrize("tag", list(CASES))
def test_full_result_matches_stata(tag):
    _check(tag, estimate_case(CASES[tag]))


@pytest.mark.parametrize("tag", ["c1", "c2", "c3", "c5"])
def test_literal_engine_gives_the_same_result(tag):
    _check(tag, estimate_case(CASES[tag], "literal"))


@pytest.mark.parametrize("tag", [t for t in CASES if t.startswith("gb")])
def test_bootstrap_p_value_is_a_multiple_of_one_over_b(tag):
    fit = estimate_case(CASES[tag])
    assert fit.boot_reps == BOOT
    assert fit.boot_sup.shape == (BOOT,)
    assert abs(fit.boots_p * BOOT - round(fit.boots_p * BOOT)) < 1e-9


@pytest.mark.parametrize("tag", [t for t in CASES if t.startswith("gb")])
def test_injected_draws_give_the_same_p_value_as_the_seed(tag):
    case = CASES[tag]
    data = case_data(case)
    draws = StataRNG(case.seed).normal((case.boost, data.n_units))
    fit = estimate(
        data, static=case.static, kink=case.kink, grid_num=case.grid_num,
        trim_rate=case.trim_rate, boot_reps=case.boost, draws=draws,
    )  # fmt: skip
    assert fit.boots_p == pytest.approx(float(np.ravel(FROZEN[tag]["scal"])[2]), abs=5e-5)


def test_no_bootstrap_gives_minus_one_and_a_read_only_result():
    fit = estimate_case(CASES["c1"])
    assert fit.boots_p == -1.0
    assert fit.boot_sup.size == 0
    assert np.isnan(fit.sup_wald)
    assert not fit.coef.flags.writeable
    with pytest.raises(ValueError):
        fit.cov[0, 0] = 0.0
