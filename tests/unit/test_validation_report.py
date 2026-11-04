"""The validation report is built from the deviations the golden tests record."""

from validation import report


def record(case, obj, n=1, abs_=0.0, margin=0.0, module="test_point_golden", rtol=None):
    return report.Record(module, case, obj, n, abs_, margin, rtol)


def test_a_case_is_the_parameter_of_the_test_or_its_name():
    assert report.case_name("test_confidence_set_matches_stata[fd_jump]") == "fd_jump"
    assert report.case_name("test_objtol_against_stata") == "objtol_against_stata"


def test_latex_special_characters_are_escaped():
    assert report.tex("e(ci_grid) & 50%") == r"e(ci\_grid) \& 50\%"
    assert report.dev(0) == "0"
    assert report.dev(1.24e-9) == r"$1.2\times10^{-9}$"


def test_summary_counts_cases_objects_and_values_and_keeps_the_worst_deviation():
    rows = [record("a", "e(b)", 9, 1e-9, 0.01), record("a", "e(V)", 81, 3e-8, 0.2),
            record("b", "e(b)", 9, 2e-10, 0.003)]  # fmt: skip
    block = report.summarise(rows)["test_point_golden"]
    assert (block["cases"], block["objects"], block["values"]) == (2, 2, 99)
    assert block["abs"] == 3e-8 and block["margin"] == 0.2


def test_a_declared_looser_tolerance_stays_out_of_the_summary_and_is_listed_apart():
    rows = [record("a", "e(b)", abs_=1e-9), record("cond13", "invsym", abs_=6e2, rtol=1e-3)]
    assert report.summarise(rows)["test_point_golden"]["abs"] == 1e-9
    assert [case for case, *_ in report.by_case(rows)] == ["a"]
    assert "cond13" in report._relaxed_section([rows[1]])
    assert "No comparison" in report._relaxed_section([])


def test_by_case_names_the_object_that_deviates_most():
    rows = [record("a", "e(b)", abs_=1e-9), record("a", "e(V)", abs_=5e-8)]
    ((case, objects, values, worst, size),) = report.by_case(rows)
    assert (case, objects, values, worst, size) == ("a", 2, 2, "e(V)", 5e-8)


def test_every_recorded_comparison_agrees_with_stata_under_the_rule_of_the_project():
    records = report.load()
    assert len(records) > 4000
    strict = [r for r in records if r.rtol is None]
    assert all(r.margin <= 1 for r in strict), [r for r in strict if r.margin > 1][:3]
    relaxed = [r for r in records if r.rtol is not None]
    assert {r.case for r in relaxed} == {"cond13"}  # the one declared exception


def test_the_report_covers_every_block_of_golden_tests_that_compares_numbers():
    modules = {r.module for r in report.load()}
    assert modules <= set(report.BLOCKS)
    assert len(modules) >= 20


def test_the_appendix_is_a_fragment_of_the_guide_not_a_document(tmp_path):
    path = report.build(tmp_path / "appendix.tex")
    tex = path.read_text(encoding="utf-8")
    assert r"\documentclass" not in tex and r"\begin{document}" not in tex
    assert r"\section{Validation against Stata 17}" in tex and "app:validation" in tex
    assert r"\subsection{Summary by block}" in tex
    assert "Comparisons under a looser tolerance" in tex
    assert r"\code{" not in tex  # the macro of the note takes verbatim text, this one does not
    assert tex.count(r"\begin{longtable}") == tex.count(r"\end{longtable}")
