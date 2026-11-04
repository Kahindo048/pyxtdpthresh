"""The public API is documented, and the examples of its docstrings run (K.2.5)."""

import doctest
import inspect
import sys
from pathlib import Path

import matplotlib
import pytest

matplotlib.use("Agg")

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools import check_docstrings  # noqa: E402

import pyxtdpthresh as pyx  # noqa: E402


def test_every_public_name_has_a_summary_its_parameters_and_its_returns():
    assert check_docstrings.audit() == []


def test_the_audit_sees_a_missing_parameter_and_a_missing_returns_section():
    def f(a, b):
        """Summary.

        Parameters
        ----------
        a
            Described.
        """
        return a + b

    f.__annotations__["return"] = "int"
    gaps = list(check_docstrings.audit_callable("f", f))
    assert gaps == ["f: parameters not described: b", "f: no Returns section"]


def test_the_sections_of_a_docstring_are_split_by_title():
    doc = "Summary.\n\nParameters\n----------\na, b : int\n    Both.\n\nReturns\n-------\nint"
    parts = check_docstrings.sections(doc)
    assert parts[""].strip() == "Summary."
    assert check_docstrings.documented_names(parts["Parameters"]) == {"a", "b"}


@pytest.mark.slow
def test_the_examples_of_the_public_docstrings_run_and_print_what_they_say():
    finder = doctest.DocTestFinder(recurse=False)
    runner = doctest.DocTestRunner(optionflags=doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE)
    tested = 0
    for name in pyx.__all__:
        if name == "__version__":
            continue
        obj = getattr(pyx, name)
        if not (inspect.isfunction(obj) or inspect.isclass(obj)):
            continue
        for test in finder.find(obj, name, globs={}):
            if test.examples:
                runner.run(test)
                tested += 1
    result = runner.summarize(verbose=False)
    assert result.failed == 0, f"{result.failed} of {result.attempted} examples failed"
    assert tested >= 12 and result.attempted >= 40
