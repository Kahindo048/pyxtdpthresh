"""Tables, summaries and exports of a fit (block I.2): they carry the validated numbers exactly."""

import csv
import json
import logging
import math
import shutil
import subprocess
import sys
import warnings
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from reference_spec import SPEC
from scipy.stats import norm
from test_search import simulate

from pyxtdpthresh._errors import DataError, PyxdpthreshError, PyxdpthreshWarning, SpecificationError
from pyxtdpthresh.extras.reporting import (
    ThresholdStargazer,
    ci_table,
    compare,
    regime_table,
    summary,
    to_dataframe,
    to_json,
)
from pyxtdpthresh.extras.reporting.escape import latex, markdown, web
from pyxtdpthresh.extras.reporting.extract import extract
from pyxtdpthresh.extras.reporting.formats import number, star_count, star_note
from pyxtdpthresh.extras.reporting.renderers import csv as csv_renderer
from pyxtdpthresh.extras.reporting.renderers import html, text
from pyxtdpthresh.extras.reporting.renderers import latex as latex_renderer
from pyxtdpthresh.extras.reporting.renderers import markdown as md_renderer
from pyxtdpthresh.extras.reporting.table_spec import Cell
from pyxtdpthresh.models.xtdpthresh.fit import fit_point
from pyxtdpthresh.models.xthenreg.design import prepare_data
from pyxtdpthresh.models.xthenreg.estimate import estimate as xthenreg_estimate

REFERENCE = Path(__file__).parent / "reference_tables"


def fit(df, regressors=("x",), **options):
    options = {"collapse": True, "grid": 25, "grid_ci": 25, "seed": 3, "n_boot": 49, **options}
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", PyxdpthreshWarning)
        return fit_point(df, "y", regressors, q="q", id="id", time="t", **options)


@pytest.fixture(scope="module")
def frame():
    return simulate(n=300, t=7, seed=4)


@pytest.fixture(scope="module")
def fd(frame):
    return fit(frame)


@pytest.fixture(scope="module")
def fod(frame):
    return fit(frame, method="fod")


@pytest.fixture(scope="module")
def kink(frame):
    return fit(simulate(n=300, t=7, seed=4, kink=True), ("x", "q"), kink=True)


@pytest.fixture(scope="module")
def henreg(frame):
    data = prepare_data(frame, "y", "q", ["x"], id="id", time="t")
    return xthenreg_estimate(data, grid_num=25, boot_reps=49, seed=3)


@pytest.fixture(scope="module")
def point_only(frame):
    return fit(frame, bootstrap=False)


# --------------------------------------------------------------------------------- formats
def test_numbers_have_no_negative_zero_and_the_decimal_sign_of_the_language():
    assert number(-0.0004, 3) == "0.000"
    assert number(-1.23456, 2) == "-1.23"
    assert number(1.5, 2, ",") == "1,50"
    assert number(float("nan")) == "-" and number(None) == "-"


def test_stars_count_the_levels_a_p_value_is_strictly_under():
    assert [star_count(p) for p in (0.2, 0.1, 0.07, 0.04, 0.009, 0.01, math.nan)] == [
        0, 0, 1, 2, 3, 2, 0,
    ]  # fmt: skip
    assert star_count(0.03, (0.05,)) == 1
    assert star_note() == "*p<0.1; **p<0.05; ***p<0.01"
    assert star_note((0.05, 0.01), ",") == "*p<0,05; **p<0,01"


def test_escaping_protects_each_format():
    assert latex("a_b & 50% #1 {x}") == r"a\_b \& 50\% \#1 \{x\}"
    assert latex("γ̂ and γ") == r"$\hat{\gamma}$ and $\gamma$"
    assert latex("p<0.1") == r"p\textless{}0.1"
    assert markdown("a*b_c|d") == r"a\*b\_c\|d"
    assert web("a<b & c") == "a&lt;b &amp; c"


# ------------------------------------------------------------------------------ extraction
def test_extraction_of_an_xtdpthresh_fit_carries_its_estimates_and_diagnostics(fd):
    column = extract(fd)
    theta, se = fd.search.fit.theta, np.sqrt(np.diag(fd.cov))
    for position, name in enumerate(fd.names):
        block, _, variable = name.partition(":")
        assert column.coefs[(block, variable)].b == theta[position]
        assert column.coefs[(block, variable)].se == se[position]
    upper = fd.upper
    for position, name in enumerate(upper.names):
        est = column.coefs[("upper", name.partition(":")[2])]
        assert est.b == upper.b[position]
    stats = column.stats
    assert stats["gamma"] == fd.search.fit.gamma
    assert stats["n_obs"] == fd.n_obs and stats["n_units"] == fd.n_units
    assert stats["hansen_p"] == fd.hansen.p_value
    assert stats["linearity_p"] == fd.bootstrap.linearity.p_value
    assert stats["gamma_ci"] == (fd.bootstrap.ci.lo, fd.bootstrap.ci.hi)
    assert column.q == "q" and column.dep_var == "y"


def test_the_labels_of_an_xthenreg_fit_follow_stata_and_match_the_coefficients(frame):
    data = prepare_data(frame, "y", "q", ["x"], id="id", time="t")
    for static, kink in ((False, False), (True, False), (False, True), (True, True)):
        result = xthenreg_estimate(data, static=static, kink=kink, grid_num=15)
        assert len(result.names) == result.coef.size
        assert result.names[-1] == "r" and result.y_name == "y" and result.q_name == "q"
    jump = xthenreg_estimate(data, grid_num=15)
    assert jump.names == ("Lag_y_b", "x_b", "cons_d", "Lag_y_d", "x_d", "r")
    assert xthenreg_estimate(data, kink=True, grid_num=15).names[-2:] == ("kink_slope", "r")


def test_an_xthenreg_upper_slope_is_the_sum_with_its_own_standard_error(henreg):
    column = extract(henreg)
    names = henreg.names
    lo, ch = names.index("x_b"), names.index("x_d")
    upper = column.coefs[("upper", "x")]
    assert upper.b == pytest.approx(henreg.coef[lo] + henreg.coef[ch])
    variance = henreg.cov[lo, lo] + henreg.cov[ch, ch] + 2 * henreg.cov[lo, ch]
    assert upper.se == pytest.approx(math.sqrt(variance))
    assert column.coefs[("lower", "L.y")].b == henreg.coef[0]
    assert ("change", "_cons") in column.coefs
    assert column.stats["gamma_ci"] == tuple(henreg.ci[-1])


def test_an_unknown_result_type_is_refused_with_its_key():
    with pytest.raises(SpecificationError) as caught:
        extract(object())
    assert caught.value.key == "table_unknown_model"


# -------------------------------------------------------------------- coefficient cells
def test_each_statistic_under_the_estimate_is_computed_from_b_and_se(fd):
    column = extract(fd)
    est = column.coefs[("lower", "x")]
    z = est.b / est.se
    p = 2 * norm.sf(abs(z))
    for statistic, expected in (
        ("se", f"({est.se:.3f})"),
        ("t", f"({z:.3f})"),
        ("p", f"({p:.3f})"),
        ("ci", f"[{est.b - norm.ppf(0.975) * est.se:.3f}, {est.b + norm.ppf(0.975) * est.se:.3f}]"),
    ):
        table = ThresholdStargazer([fd], statistic=statistic, keep=r"^x$", omit="change|upper")
        row = table.spec.rows[0]
        assert row.cells[0].below == expected.replace("-0.000", "0.000")
        assert row.cells[0].text == f"{est.b:.3f}"


def test_the_ci_statistic_follows_the_level_and_the_digits(fd):
    est = extract(fd).coefs[("lower", "x")]
    z = norm.ppf(0.95)
    table = ThresholdStargazer(
        [fd], statistic="ci", level=90, digits=2, keep="^x$", omit="change|upper"
    )
    expected = f"[{est.b - z * est.se:.2f}, {est.b + z * est.se:.2f}]"
    assert table.spec.rows[0].cells[0].below == expected
    assert "90 % confidence intervals" in table.spec.notes[1]


def test_stars_follow_the_chosen_levels(fd):
    est = extract(fd).coefs[("upper", "x")]
    p = 2 * norm.sf(abs(est.b / est.se))
    loose = ThresholdStargazer([fd], keep="upper:x", star_levels=(0.5, 0.2, 1e-30))
    assert loose.spec.rows[0].cells[0].stars == star_count(p, (0.5, 0.2, 1e-30))
    assert loose.spec.notes[0].startswith("*p<0.5; **p<0.2; ***p<1e-30")


# -------------------------------------------------------------------- table construction
def test_the_rows_are_the_union_of_the_models_by_regime(fd, kink, henreg):
    table = ThresholdStargazer([fd, kink, henreg], ["FD", "kink", "xthenreg"])
    keys = [(r.block, r.label) for r in table.spec.rows]
    blocks = [b for b, _ in keys]
    assert blocks == sorted(
        blocks, key=["Lower regime", "Change at the threshold", "Upper regime"].index
    )
    assert ("Change at the threshold", "q") in keys  # the kink model's slope change
    assert ("Change at the threshold", "_cons") in keys
    kink_column = 1
    row = next(
        r for r in table.spec.rows if (r.block, r.label) == ("Change at the threshold", "_cons")
    )
    assert row.cells[kink_column] == Cell()  # a kink model has no jump in the level


def test_keep_omit_order_and_labels_select_name_and_sort_the_rows(fd):
    table = ThresholdStargazer(
        [fd], keep=["x", "_cons"], omit=r"^change:x$", order=["x"],
        covariate_labels={"x": "Cash flow", "change:_cons": "Intercept shift"},
    )  # fmt: skip
    labels = [(r.block, r.label) for r in table.spec.rows]
    assert labels == [
        ("Lower regime", "Cash flow"),
        ("Change at the threshold", "Intercept shift"),
        ("Upper regime", "Cash flow"),
    ]


def test_columns_dependent_variable_added_lines_notes_and_stat_options(fd, fod):
    table = ThresholdStargazer(
        [fd, fod], ["FD", "FOD"], column_labels=["one", "two"], dep_var_label="Investment",
        add_lines=[("Firm effects", ["Yes", "Yes"])], notes=["Own note."], title="T", label="tab:t",
        font_size="small", omit_stat=["n_obs", "hansen_p"],
    )  # fmt: skip
    spec = table.spec
    assert spec.columns == ("FD", "FOD") and spec.column_labels == ("one", "two")
    assert spec.dep_vars == ("Investment", "Investment")
    assert spec.stats[0].label == "Firm effects" and spec.stats[0].values == ("Yes", "Yes")
    shown = [s.label for s in spec.stats]
    assert "Observations" not in shown and "Hansen J (p-value)" not in shown
    assert spec.notes[-1] == "Own note."
    assert (spec.title, spec.label, spec.font_size) == ("T", "tab:t", "small")
    default = ThresholdStargazer([fd, fod]).spec
    assert default.columns == ("(1)", "(2)")


def test_diagnostics_are_missing_for_the_models_that_have_none(fd, henreg):
    table = ThresholdStargazer([fd, henreg])
    rows = {s.label: s.values for s in table.spec.stats}
    assert rows["Hansen J (p-value)"][1] == "-" and rows["Hansen J (p-value)"][0] != "-"
    assert rows["Observations"][1] == "-"
    assert rows["Threshold effect"] == ("jump", "jump")
    assert rows["Transformation"] == ("FD", "FD")
    assert any("grid bootstrap" in n for n in table.spec.notes)  # intervals of different kinds
    assert not any("grid bootstrap" in n for n in ThresholdStargazer([fd]).spec.notes)


def test_a_table_without_bootstrap_has_no_interval_or_linearity_line(point_only):
    labels = [s.label for s in ThresholdStargazer([point_only]).spec.stats]
    assert "Linearity test (p-value)" not in labels
    assert not any("interval" in label for label in labels)


def test_single_row_puts_the_statistic_on_the_line_of_the_estimate(fd):
    table = ThresholdStargazer([fd], single_row=True, keep="lower:x")
    cell = table.spec.rows[0].cells[0]
    assert (
        table.spec.lines()[-len(table.spec.stats) - len(table.spec.notes) - 1][1] == cell.inline()
    )
    assert "(" in cell.inline()
    assert len([ln for ln in table.to_text().splitlines() if ln.startswith("x")]) == 1


def test_the_french_table_has_french_labels_and_decimal_commas(fd):
    table = ThresholdStargazer([fd], lang="fr", keep="lower:x")
    assert table.spec.dep_var_label == "Variable dépendante"
    assert table.spec.rows[0].block == "Régime bas"
    assert "," in table.spec.rows[0].cells[0].text and "." not in table.spec.rows[0].cells[0].text
    assert table.spec.notes[0].startswith("*p<0,1")
    assert any(s.label.startswith("J de Hansen") for s in table.spec.stats)


def test_bad_arguments_are_refused_with_their_keys(fd):
    cases = [
        (dict(models=[]), "table_no_models"),
        (dict(models=[fd], statistic="z"), "table_statistic"),
        (dict(models=[fd], model_names=["a", "b"]), "table_names_length"),
        (dict(models=[fd], column_labels=["a", "b"]), "table_names_length"),
        (dict(models=[fd], add_lines=[("x", ["1", "2"])]), "table_names_length"),
    ]
    for arguments, key in cases:
        with pytest.raises(SpecificationError) as caught:
            ThresholdStargazer(**arguments)
        assert caught.value.key == key


# -------------------------------------------------------------------------- renderings
def test_renderings_equal_the_reference_files():
    for module, name in (
        (latex_renderer, "table.tex"),
        (html, "table.html"),
        (md_renderer, "table.md"),
        (text, "table.txt"),
        (csv_renderer, "table.csv"),
    ):
        expected = (REFERENCE / name).read_text(encoding="utf-8")
        assert module.render(SPEC) == expected, name


def test_the_latex_table_is_booktabs_with_math_stars_and_escaped_text():
    out = latex_renderer.render(SPEC)
    assert out.count(r"\toprule") == out.count(r"\bottomrule") == 1
    assert r"0.306$^{***}$" in out and r"$-$0.967" in out
    assert r"\caption{Results \& 50\%}" in out and r"\label{tab:main}" in out
    assert out.count(r"\begin{tabular}") == out.count(r"\end{tabular}") == 1


def test_csv_text_reads_back_as_the_lines_of_the_table(fd, henreg):
    table = ThresholdStargazer([fd, henreg], ["FD", "xthenreg"])
    rows = list(csv.reader(table.to_csv().splitlines()))
    assert rows == table.spec.lines()


def test_word_file_reads_back_with_the_cells_of_the_table(fd, fod, tmp_path):
    docx = pytest.importorskip("docx")
    table = ThresholdStargazer([fd, fod], ["FD", "FOD"], title="Word table")
    path = table.to_word(tmp_path / "t.docx")
    document = docx.Document(str(path))
    cells = [[c.text for c in row.cells] for row in document.tables[0].rows]
    lines = table.spec.lines()
    assert cells == lines[: len(cells)]
    assert document.paragraphs[0].text == "Word table"
    assert [p.text for p in document.paragraphs[1:] if p.text] == list(table.spec.notes)


def test_excel_file_reads_back_with_the_cells_of_the_table(fd, fod, tmp_path):
    openpyxl = pytest.importorskip("openpyxl")
    table = ThresholdStargazer([fd, fod], ["FD", "FOD"])
    path = table.to_excel(tmp_path / "t.xlsx")
    sheet = openpyxl.load_workbook(path).active
    got = [["" if c is None else str(c) for c in row] for row in sheet.iter_rows(values_only=True)]
    assert got == table.spec.lines()


def test_a_missing_export_package_names_the_install_command(fd, tmp_path, monkeypatch):
    monkeypatch.setitem(sys.modules, "docx", None)
    monkeypatch.setitem(sys.modules, "openpyxl", None)
    table = ThresholdStargazer([fd])
    for method, package in ((table.to_word, "python-docx"), (table.to_excel, "openpyxl")):
        with pytest.raises(PyxdpthreshError) as caught:
            method(tmp_path / "t.out")
        assert caught.value.key == "table_missing_package"
        assert package in str(caught.value) and "pip install" in str(caught.value)


def test_exports_write_files_log_and_never_print(fd, tmp_path, capsys, caplog):
    table = ThresholdStargazer([fd])
    with caplog.at_level(logging.INFO, logger="pyxtdpthresh.extras.reporting.stargazer"):
        table.to_latex(tmp_path / "t.tex")
        table.to_html(tmp_path / "t.html")
        table.to_markdown(tmp_path / "t.md")
        table.to_csv(tmp_path / "t.csv")
        table.to_text(tmp_path / "t.txt")
    assert capsys.readouterr().out == ""
    assert len(caplog.records) == 5
    assert (tmp_path / "t.tex").read_text(encoding="utf-8") == table.to_latex()


def test_jupyter_and_print_use_the_same_engine(fd):
    table = ThresholdStargazer([fd])
    assert table._repr_html_() == table.to_html() and "<table" in table._repr_html_()
    assert table._repr_latex_() == table.to_latex()
    assert str(table) == table.to_text()


def test_the_console_text_falls_back_to_ascii_when_it_cannot_encode_greek(fd, monkeypatch):
    class Narrow:
        encoding = "cp1252"

    monkeypatch.setattr(sys, "stdout", Narrow())
    out = ThresholdStargazer([fd]).to_text()
    assert "gamma-hat" in out and "γ" not in out


@pytest.mark.skipif(shutil.which("pdflatex") is None, reason="pdflatex is not installed")
def test_the_latex_table_compiles_with_pdflatex(fd, henreg, tmp_path):
    body = ThresholdStargazer([fd, henreg], ["FD", "xthenreg"], title="Compiled").to_latex()
    source = "\\documentclass{article}\n\\usepackage{booktabs}\n\\begin{document}\n" + body
    (tmp_path / "t.tex").write_text(source + "\\end{document}\n", encoding="utf-8")
    try:
        run = subprocess.run(
            ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "t.tex"],
            cwd=tmp_path, capture_output=True, text=True, timeout=180, check=False,
        )  # fmt: skip
    except subprocess.TimeoutExpired:
        pytest.skip("pdflatex did not finish (a package is probably being installed)")
    if "File `booktabs.sty' not found" in run.stdout:
        pytest.skip("the booktabs package is not installed")
    assert run.returncode == 0, run.stdout[-1500:]
    assert (tmp_path / "t.pdf").exists()


# ------------------------------------------------------------------------ data frames
def test_the_coefficient_frame_holds_the_validated_estimates(fd):
    frame = to_dataframe(fd)
    theta, se = fd.search.fit.theta, np.sqrt(np.diag(fd.cov))
    for position, name in enumerate(fd.names):
        block, _, variable = name.partition(":")
        row = frame.loc[(block, variable)]
        assert row["estimate"] == theta[position] and row["se"] == se[position]
        assert row["z"] == pytest.approx(theta[position] / se[position])
        assert row["p"] == pytest.approx(2 * norm.sf(abs(theta[position] / se[position])))
        assert row["ci_low"] == pytest.approx(theta[position] - norm.ppf(0.975) * se[position])
    gamma = frame.loc[("threshold", "gamma")]
    assert gamma["estimate"] == fd.search.fit.gamma
    assert (gamma["ci_low"], gamma["ci_high"]) == (fd.bootstrap.ci.lo, fd.bootstrap.ci.hi)
    assert frame.attrs["level"] == 95.0
    narrow = to_dataframe(fd, level=80).drop(index="threshold", level="block")
    wide = frame.drop(index="threshold", level="block")
    assert ((narrow["ci_high"] - narrow["ci_low"]) < (wide["ci_high"] - wide["ci_low"])).all()


def test_the_ci_table_is_e_ci_grid_with_integer_codes(fd, point_only):
    table = ci_table(fd)
    np.testing.assert_array_equal(table.to_numpy(dtype=float), fd.bootstrap.ci.table)
    assert list(table.columns) == [
        "gamma",
        "statistic",
        "critical",
        "accepted",
        "n_valid",
        "status",
    ]
    assert str(table["status"].dtype) == "Int64"
    with pytest.raises(DataError) as caught:
        ci_table(point_only)
    assert caught.value.key == "table_needs_bootstrap"


def test_the_regime_table_counts_and_averages_the_equations_of_each_regime(fd):
    table = regime_table(fd)
    stack = fd.stack
    q = stack.level_q[stack.current_level]
    upper = q > fd.search.fit.gamma
    assert table.loc["upper", "observations"] == upper.sum()
    assert table.loc["lower", "observations"] == (~upper).sum()
    assert table["observations"].sum() == len(q) and table["share"].sum() == pytest.approx(100.0)
    assert table.loc["upper", "units"] == np.unique(stack.unit[upper]).size
    assert table.loc["upper", "q"] == pytest.approx(q[upper].mean())
    assert table.loc["lower", "y"] == pytest.approx(fd.data.y[stack.row][~upper].mean())
    x_level = stack.level_x[stack.current_level][:, 1]
    assert table.loc["lower", "x"] == pytest.approx(x_level[~upper].mean())
    assert list(table.columns)[:3] == ["observations", "units", "share"]


# ------------------------------------------------------------------------------ JSON
def test_the_json_record_is_reproducible_and_strict(fd, tmp_path):
    path = tmp_path / "fit.json"
    text_ = to_json(fd, path)
    record = json.loads(path.read_text(encoding="utf-8"))
    assert json.loads(text_) == record
    assert record["model"] == "xtdpthresh"
    assert record["specification"] == {"y": "y", "q": "q", "x": ["x"], "id": "id", "time": "t"}
    assert record["options"]["seed"] == 3 and record["options"]["n_boot"] == 49
    assert record["options"]["maxlag"] == [1, "inf"]  # infinity survives as a string
    assert record["scalars"]["rseed"] == 3 and record["scalars"]["gamma"] == fd.search.fit.gamma
    assert record["ci_grid"]["columns"][0] == "gamma"
    assert np.array(record["ci_grid"]["rows"]).shape == fd.bootstrap.ci.table.shape
    versions = record["environment"]
    assert {"pyxtdpthresh", "python", "numpy", "scipy", "pandas"} <= set(versions)
    assert any(c["block"] == "threshold" for c in record["coefficients"])
    json.loads(text_, parse_constant=lambda c: pytest.fail(f"non-standard constant {c}"))


def test_the_json_of_a_fit_without_bootstrap_has_nulls_not_nan(point_only):
    text_ = to_json(point_only)
    assert "NaN" not in text_ and "Infinity" not in text_.replace('"inf"', "")
    record = json.loads(text_)
    assert record["scalars"]["pval_lin"] is None and "ci_grid" not in record


def test_the_json_record_of_an_xthenreg_fit(henreg):
    record = json.loads(to_json(henreg))
    assert record["model"] == "xthenreg"
    assert record["specification"]["names"] == list(henreg.names)
    assert record["scalars"]["gamma"] == henreg.gamma
    np.testing.assert_allclose(record["cov"], henreg.cov)
    assert record["options"]["boot_reps"] == 49


# ------------------------------------------------------------------------------ summary
def _section(out, title):
    """Lines of the table that starts with ``title`` (up to the closing double rule)."""
    lines = out.splitlines()
    start = next(i for i, line in enumerate(lines) if line.strip().startswith(title))
    end = next(i for i in range(start + 2, len(lines)) if lines[i] == "=" * len(lines[start + 1]))
    return lines[start : end + 1]


def test_the_summary_has_the_six_blocks_of_pyxtabond2_and_pyxthreg(fd):
    out = summary(fd, when=datetime(2026, 11, 4, 10, 12, 31))
    lines = out.splitlines()
    assert lines[0].strip() == "PyXtdpthresh Estimation Results"
    assert "Date:" in out and "Wed, 04 Nov 2026" in out and "10:12:31" in out
    for title in (
        "Threshold Estimates (Level = 95%)",
        "Threshold Effect Test (Bootstrap, B = 49)",
        "Dynamic Panel Threshold Coefficients",
        "Diagnostic Tests",
    ):
        assert any(line.strip() == title for line in lines)
    assert max(len(line) for line in lines) <= 80
    assert out.endswith("=" * 80 + "\n")


def test_the_summary_numbers_are_the_ones_of_the_fit(fd):
    out = summary(fd)
    boot = fd.bootstrap
    th = _section(out, "Threshold Estimates")[-2].split()
    assert th[1] == f"{fd.search.fit.gamma:.4f}"
    assert (th[2], th[3]) == (f"{boot.ci.lo:.4f}", f"{boot.ci.hi:.4f}")
    test = _section(out, "Threshold Effect Test")[-2].split()
    assert test[1] == f"{boot.linearity.statistic:.4f}"
    assert test[2] == f"{boot.linearity.p_value:.4f}"
    diag = "\n".join(_section(out, "Diagnostic Tests"))
    assert f"z = {fd.serial.ar1.statistic:.2f}" in diag
    assert f"Pr > z = {fd.serial.ar2.p_value:.3f}" in diag
    assert f"chi2({fd.hansen.df:.0f}) = {fd.hansen.statistic:.2f}" in diag
    assert f"Pr > chi2 = {fd.hansen.p_value:.3f}" in diag
    est = extract(fd).coefs[("upper", "x")]
    assert f"{est.b:.4f}" in out and f"{est.se:.4f}" in out
    for block in ("Lower regime  (q <= ", "Change at the threshold", "Upper regime  (q > "):
        assert block in out


def test_the_critical_values_are_the_order_statistics_the_p_value_counts(fd):
    draws = np.sort(fd.bootstrap.linearity.draws)[::-1]
    b = draws.size
    col = extract(fd).stats
    for suffix, size in (("10", 0.10), ("5", 0.05), ("1", 0.01)):
        k = int(size * (b + 1) + 1e-9)
        want = float(draws[k - 1]) if k >= 1 else None
        assert col[f"linearity_crit{suffix}"] == want
    # a statistic above the critical value of size a has a bootstrap p-value of at most a
    if fd.bootstrap.linearity.statistic > col["linearity_crit5"]:
        assert fd.bootstrap.linearity.p_value <= 0.05


def test_a_size_with_too_few_draws_has_no_critical_value(fd):
    from pyxtdpthresh.extras.reporting.extract import _critical_values

    out = _critical_values(np.arange(20.0), "linearity")
    assert out["linearity_crit1"] is None and out["linearity_crit10"] == 18.0


def test_the_summary_in_french_and_at_another_level(fd):
    out = summary(fd, lang="fr", level=90)
    assert "Résultats d'estimation PyXtdpthresh" in out and "Régime haut" in out
    assert "[0.050" in out and "0.950]" in out and "Tests de diagnostic" in out
    assert max(len(line) for line in out.splitlines()) <= 80


def test_the_summary_of_xthenreg_has_dashes_where_the_model_has_nothing(henreg):
    out = summary(henreg)
    assert out.splitlines()[0].strip() == "PyXthenreg Estimation Results"
    assert "Linearity (sup-Wald)" in out and f"{henreg.sup_wald:.4f}" in out
    assert all(row.split()[-1] == "-" for row in _section(out, "Diagnostic Tests")[4:7])
    assert max(len(line) for line in out.splitlines()) <= 80


def test_the_summary_without_bootstrap_has_no_threshold_effect_table(point_only):
    out = summary(point_only)
    assert "Threshold Effect Test" not in out
    th = _section(out, "Threshold Estimates")[-2].split()
    assert th[2:] == ["-", "-"]


def test_long_variable_names_widen_every_rule(frame):
    long = frame.rename(columns={"x": "a_very_long_regressor_name_for_the_table"})
    out = summary(fit(long, ("a_very_long_regressor_name_for_the_table",)))
    widths = {len(line) for line in out.splitlines() if line and set(line) == {"="}}
    assert len(widths) == 1 and widths.pop() > 80


def test_compare_is_the_stargazer_shortcut(fd, fod):
    assert (
        compare([fd, fod], model_names=["a", "b"]).spec
        == ThresholdStargazer([fd, fod], ["a", "b"]).spec
    )


def test_the_reporting_layer_returns_tables_it_does_not_estimate(fd):
    before = fd.search.fit.theta.copy()
    ThresholdStargazer([fd]).to_latex()
    summary(fd)
    regime_table(fd)
    np.testing.assert_array_equal(fd.search.fit.theta, before)
    assert isinstance(to_dataframe(fd), pd.DataFrame)
