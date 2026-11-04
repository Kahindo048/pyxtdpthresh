"""The examples of the help file of ``xtdpthresh`` against Stata 17, as written.

Every object the examples produce (coefficients, standard errors, the scalars and matrices of
``e()``, the confidence sets, the tests and what ``predict`` returns) must agree to four decimals.
"""

import pytest
from validation import help_examples as he

pytestmark = pytest.mark.golden

FROZEN = he.frozen()
_ROWS: dict[str, list[he.Row]] = {}


def rows(name):
    """Comparison of one example, once per session."""
    if not _ROWS:
        _ROWS.update(he.run_all())
    return _ROWS[name]


@pytest.mark.parametrize("example", he.EXAMPLES, ids=lambda e: e.name)
def test_the_python_call_is_the_command_of_the_help(example):
    assert he.canonical(he.command_from_args(example)) == he.canonical(example.stata)


@pytest.mark.parametrize("example", he.EXAMPLES, ids=lambda e: e.name)
def test_stata_accepted_the_command(example):
    ref = FROZEN[example.name]
    assert ref["rc"] == 0, ref["text"]
    assert ref["command"] == example.stata


@pytest.mark.parametrize("example", he.EXAMPLES, ids=lambda e: e.name)
def test_every_object_agrees_with_stata(example):
    bad = [r for r in rows(example.name) if not r.ok]
    detail = "; ".join(f"{r.group} {r.name}: {r.python} vs {r.stata}" for r in bad[:6])
    assert not bad, f"{len(bad)} objects differ: {detail}"


def test_the_examples_compare_a_good_number_of_objects():
    assert all(len(rows(e.name)) >= 50 for e in he.EXAMPLES)


def test_the_published_tables_are_current():
    _ = rows("point")
    assert he.REPORT.read_text(encoding="utf-8") == he.report(_ROWS)
