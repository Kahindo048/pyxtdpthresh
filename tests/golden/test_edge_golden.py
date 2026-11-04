"""Edge cases of ``xtdpthresh`` against Stata 17: same return code, same estimates (K.1.4)."""

import gzip
import io
import json
import math
import warnings
from pathlib import Path

import pandas as pd
import pytest

from pyxtdpthresh import xtdpthresh
from pyxtdpthresh._errors import PyxdpthreshError

GOLDEN = json.loads((Path(__file__).parent / "edge_golden.json").read_text(encoding="utf-8"))
CASES = GOLDEN["cases"]
PANELS = pd.read_csv(
    io.BytesIO(gzip.decompress((Path(__file__).parent / "edge_panels.csv.gz").read_bytes()))
)

#: The call of each case (the panels and these options are written by ``validation/edge_cases.py``).
ARGS = {
    "min_n1_t5": {"bootstrap": False},
    "min_n2_t4": {"bootstrap": False},
    "min_n3_t3": {"bootstrap": False},
    "min_n4_t4": {"bootstrap": False},
    "min_n5_t2": {"bootstrap": False},
    "min_n20_t3": {"bootstrap": False},
    "minregime_huge": {"bootstrap": False, "min_regime": 10_000},
    "trim_049": {"bootstrap": False, "trim": 0.49},
    "q_constant": {"bootstrap": False},
    "q_rare_ones": {"bootstrap": False},
    "q_binary": {"bootstrap": False},
    "q_four_values": {"n_boot": 99, "grid_ci": 20, "seed": 7},
    "x_duplicate": {"bootstrap": False},
    "iv_equals_x": {"bootstrap": False, "iv": ("z",)},
    "x_constant": {"bootstrap": False},
    "units_fewer_than_iv": {"bootstrap": False},
    "units_fewer_than_iv_boot": {"n_boot": 99, "grid_ci": 20, "seed": 7},
    "y_zero": {"bootstrap": False},
    "y_constant": {"bootstrap": False},
}
REGRESSORS = {"x_duplicate": ["x1", "x2"], "iv_equals_x": ["x1"], "x_constant": ["c"]}
SCALARS = {
    "gamma": lambda r: r.gamma,
    "N": lambda r: r.n_obs,
    "N_units": lambda r: r.n_units,
    "N_iv": lambda r: r.n_instruments,
    "estimator_twostep": lambda r: float(r.scalars["estimator_twostep"]),
    "gamma_lo": lambda r: r.scalars["gamma_lo"],
    "gamma_hi": lambda r: r.scalars["gamma_hi"],
}


def close(a, b):
    """Four decimals: absolute 5e-5 or relative 1e-6 (``None`` and ``nan`` are both missing)."""
    a_missing = a is None or (isinstance(a, float) and math.isnan(a))
    b_missing = b is None or (isinstance(b, float) and math.isnan(b))
    if a_missing or b_missing:
        return a_missing and b_missing
    return abs(a - b) <= 5e-5 or abs(a - b) <= 1e-6 * max(abs(a), abs(b))


def run(name):
    frame = PANELS[PANELS["case"] == name].drop(columns="case")
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        try:
            return xtdpthresh(
                frame, "y", REGRESSORS.get(name, []), q="q", id="id", time="t", **ARGS[name]
            )
        except PyxdpthreshError as error:
            return error


def test_every_case_of_the_golden_file_has_its_call():
    assert set(ARGS) == set(CASES) == set(PANELS["case"].unique())


@pytest.mark.parametrize("name", sorted(CASES))
def test_the_return_code_is_stata_s(name):
    outcome = run(name)
    expected = CASES[name]["rc"]
    if expected == 0:
        assert not isinstance(outcome, Exception), f"Stata succeeded, the package raised: {outcome}"
    else:
        assert isinstance(outcome, PyxdpthreshError), "Stata refused the case, the package did not"
        assert outcome.stata_code == expected, f"{outcome.key}: {outcome}"


@pytest.mark.parametrize("name", sorted(n for n in CASES if CASES[n]["rc"] == 0))
def test_the_estimates_are_stata_s_when_both_succeed(name):
    result = run(name)
    for key, expected in CASES[name]["scalars"].items():
        got = SCALARS[key](result)
        assert close(got, expected), f"{name}: {key} = {got}, Stata {expected}"
