"""Tables repeat the numbers validated against Stata 17 (block I.7.1).

The fits are those of the variance and bootstrap golden tests; the tables, frames and exports are
built from them and compared with the frozen ``e(b)``, ``e(V)``, ``e(b_upper)``, ``e(V_upper)``,
``e(ci_grid)`` and the interval and p-value of the threshold, to four decimals.
"""

import math

import numpy as np
import pytest
import test_bootstrap_golden as boot
import test_variance_golden as var
from validation.estimation_cases import unpack

from pyxtdpthresh.extras.reporting import ThresholdStargazer, ci_table, to_dataframe
from pyxtdpthresh.extras.reporting.labels import label

pytestmark = pytest.mark.golden

#: A table shows four decimals, so a printed value may differ from Stata's by half a unit of the
#: last digit on top of the 5e-5 of the validation.
TEXT_TOLERANCE = 1.1e-4


def printed(text):
    return float(text) if text not in ("", "-") else math.nan


def rows_of(table):
    return {(r.block, r.label): r for r in table.spec.rows}


def check_block(rows, block, names, b, se):
    shown = label(block, "en")
    for position, name in enumerate(names):
        variable = name.partition(":")[2]
        cell = rows[(shown, variable)].cells[0]
        assert printed(cell.text) == pytest.approx(b[position], abs=TEXT_TOLERANCE), name
        assert printed(cell.below.strip("()")) == pytest.approx(se[position], abs=TEXT_TOLERANCE), (
            name
        )


@pytest.mark.parametrize("name", list(var.CASES))
def test_the_table_repeats_stata_estimates_and_standard_errors(name):
    ref, fit = var.FROZEN[name], var.estimate(name)
    b, cov = unpack(ref["b"]).ravel(), unpack(ref["v"])
    se = np.sqrt(np.diag(cov))
    table = ThresholdStargazer([fit], digits=4)
    rows = rows_of(table)
    for position, full in enumerate(fit.names):
        block, _, variable = full.partition(":")
        cell = rows[(label(block, "en"), variable)].cells[0]
        assert printed(cell.text) == pytest.approx(b[position], abs=TEXT_TOLERANCE), full
        assert printed(cell.below.strip("()")) == pytest.approx(se[position], abs=TEXT_TOLERANCE)
    if var.empty(ref["bup"]):
        assert not any(block == label("upper", "en") for block, _ in rows)
        return
    upper_se = np.sqrt(np.diag(unpack(ref["vup"])))
    check_block(rows, "upper", fit.upper.names, unpack(ref["bup"]).ravel(), upper_se)


@pytest.mark.parametrize("name", list(var.CASES))
def test_the_frame_repeats_stata_estimates_to_the_validation_tolerance(name):
    ref, fit = var.FROZEN[name], var.estimate(name)
    frame = to_dataframe(fit)
    b, cov = unpack(ref["b"]).ravel(), unpack(ref["v"])
    for position, full in enumerate(fit.names):
        block, _, variable = full.partition(":")
        var.close(frame.loc[(block, variable), "estimate"], b[position], full)
        var.close(frame.loc[(block, variable), "se"], math.sqrt(cov[position, position]), full)
    var.close(frame.loc[("threshold", "gamma"), "estimate"], ref["scalars"]["gamma"], "gamma")


@pytest.mark.parametrize("name", list(boot.CASES))
def test_the_ci_table_and_the_threshold_lines_repeat_stata(name):
    ref, fit = boot.FROZEN[name], boot.estimate(name)
    sc = ref["scalars"]
    boot.close(ci_table(fit).to_numpy(dtype=float), unpack(ref["grid"]), "e(ci_grid)")
    table = ThresholdStargazer([fit], digits=4)
    lines = {s.label: s.values[0] for s in table.spec.stats}
    if not math.isnan(sc["gamma_lo"]):
        expected = f"[{sc['gamma_lo']:.4f}, {sc['gamma_hi']:.4f}]"
        got = lines[label("gamma_ci", "en", level=95.0)]
        low, high = (float(v) for v in got.strip("[]").split(","))
        assert low == pytest.approx(sc["gamma_lo"], abs=TEXT_TOLERANCE), (got, expected)
        assert high == pytest.approx(sc["gamma_hi"], abs=TEXT_TOLERANCE), (got, expected)
    if not math.isnan(sc["pval_lin"]):
        shown = lines[label("linearity_p", "en")]
        assert float(shown) == pytest.approx(sc["pval_lin"], abs=TEXT_TOLERANCE)
    assert float(lines[label("gamma", "en")]) == pytest.approx(sc["gamma"], abs=TEXT_TOLERANCE)
