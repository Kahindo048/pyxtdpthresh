"""Tests of the Stata validation tooling: case descriptions, comparison rule, frozen results."""

import numpy as np
import pytest
from validation import cases, compare, freeze


# ----------------------------------------------------------------- compare
def test_identical_arrays_pass():
    d = compare.compare_arrays("b", np.array([1.0, 2.0]), np.array([1.0, 2.0]))
    assert d.ok and d.max_abs == 0.0


def test_four_decimal_agreement_passes_and_five_fails():
    stata = np.array([0.1816947, -0.0016550])
    ok = compare.compare_arrays("b", stata + 4e-5, stata)
    bad = compare.compare_arrays("b", stata + 2e-4, stata)
    assert ok.ok
    assert not bad.ok


def test_relative_branch_accepts_large_values():
    stata = np.array([1.0e6])
    assert compare.compare_arrays("obj", stata + 0.5, stata).ok  # rel 5e-7
    assert not compare.compare_arrays("obj", stata + 50.0, stata).ok  # rel 5e-5


def test_shape_mismatch_fails_but_transposed_vector_is_accepted():
    assert not compare.compare_arrays("V", np.zeros((2, 2)), np.zeros((3, 3))).ok
    col = np.array([[1.0], [2.0], [3.0]])
    assert compare.compare_arrays("b", col.T, col).ok


def test_nan_must_match_nan():
    a = np.array([1.0, np.nan])
    assert compare.compare_arrays("x", a, a.copy()).ok
    assert not compare.compare_arrays("x", np.array([1.0, 2.0]), a).ok


def test_missing_python_object_fails_and_report_names_case():
    stata = {"b": np.array([1.0]), "V": np.array([[1.0]])}
    diffs = compare.compare_case({"b": np.array([1.0])}, stata)
    assert [d.ok for d in diffs] == [True, False]
    text = compare.report("c1", diffs)
    assert "FAIL" in text and "case c1" in text


def test_read_matrix_handles_missing_values(tmp_path):
    p = tmp_path / "x.csv"
    p.write_text("1.5,.\n2,3\n", encoding="ascii")
    m = compare.read_matrix(p)
    assert m.shape == (2, 2) and np.isnan(m[0, 1]) and m[1, 1] == 3.0


# ------------------------------------------------------------------- cases
def test_stata_command_lines():
    by_tag = {c.tag: c for c in cases.XTHENREG_CASES}
    assert by_tag["c1"].stata_command() == (
        "xthenreg invest debt, endogenous(cashflow tobin_q debt) grid_num(50) trim_rate(0.4)"
    )
    assert by_tag["c5"].stata_command().endswith("static kink")
    assert "inst(z1 z2)" in by_tag["c4"].stata_command()
    assert "exogenous(debt)" in by_tag["c3"].stata_command()


def test_case_tags_are_unique():
    tags = [c.tag for c in cases.XTHENREG_CASES]
    assert len(tags) == len(set(tags))


def test_generated_do_file_runs_every_case_and_exports_it():
    text = cases.render_xthenreg_do()
    for c in cases.XTHENREG_CASES:
        assert c.stata_command() in text
        assert f"pyx_save_xthenreg {c.tag}" in text
    assert text.rstrip().endswith("exit, clear")


def test_invest_loader_matches_the_stata_filter():
    df = cases.load_invest(max_year=1980)
    assert df["year"].max() == 1980 and df["firm"].nunique() == 565
    assert {"z1", "z2"} <= set(df.columns)
    full = cases.load_invest(max_year=None, derived=False)
    assert len(full) == 8475 and "z1" not in full.columns


# ------------------------------------------------------------ golden master
@pytest.mark.golden
def test_golden_master_is_complete_and_consistent():
    master = freeze.load_golden()
    assert "Stata 17" in master["meta"]["stata"]
    assert set(master["cases"]) == {c.tag for c in cases.XTHENREG_CASES}
    for tag, objs in master["cases"].items():
        assert {"b", "V", "CI", "scal"} <= set(objs), tag
        b = np.array(objs["b"])
        v = np.array(objs["V"])
        assert v.shape == (b.size, b.size)  # b is stored as a column
        assert np.allclose(v, v.T, atol=1e-12)
        assert np.all(np.diag(v) > 0)
        n, t, _ = np.array(objs["scal"]).ravel()
        assert (n, t) == (565, 8)
