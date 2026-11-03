"""First-difference equations on small hand-checkable panels."""

import numpy as np

from pyxtdpthresh.transforms.fd import fd_equations, previous_period_row

NAN = np.nan


def panel(times_by_unit):
    """Offsets and times of units with the given periods."""
    offsets = np.concatenate([[0], np.cumsum([len(t) for t in times_by_unit])]).astype(np.int64)
    return offsets, np.concatenate(times_by_unit).astype(np.int64)


def test_previous_period_uses_the_calendar_not_the_previous_row():
    offsets, time = panel([[1, 2, 4, 5], [2, 3]])
    got = previous_period_row(offsets, time)
    # unit 1: t=2 -> row 0; t=4 has no t=3; t=5 -> row 2.  unit 2 starts at row 4: no t=1 row.
    np.testing.assert_array_equal(got, [-1, 0, -1, 2, -1, 4])


def test_a_period_is_never_matched_across_units():
    offsets, time = panel([[3], [4]])
    np.testing.assert_array_equal(previous_period_row(offsets, time), [-1, -1])


def run(times_by_unit, eq=None, y=None, q=None, x=None):
    offsets, time = panel(times_by_unit)
    n = time.size
    return fd_equations(
        offsets,
        time,
        np.ones(n, bool) if eq is None else np.asarray(eq, bool),
        np.arange(n, dtype=float) if y is None else np.asarray(y, float),
        np.ones(n) if q is None else np.asarray(q, float),
        np.ones((n, 1)) if x is None else np.asarray(x, float).reshape(n, 1),
    )


def test_consecutive_periods_form_equations_in_unit_then_time_order():
    eqs = run([[1, 2, 3], [1, 2]])
    np.testing.assert_array_equal(eqs.row, [1, 2, 4])
    np.testing.assert_array_equal(eqs.prev, [0, 1, 3])
    np.testing.assert_array_equal(eqs.unit, [0, 0, 1])
    np.testing.assert_array_equal(eqs.unit_ptr, [0, 2, 3])
    np.testing.assert_array_equal(eqs.pair_lev, [1, 0, 2, 1, 4, 3])
    np.testing.assert_array_equal(eqs.pair_w, [1, -1, 1, -1, 1, -1])
    np.testing.assert_array_equal(eqs.pair_ptr, [0, 2, 4, 6])


def test_history_only_rows_are_levels_but_never_equations():
    # row 1 is history only: it forms no equation, and no equation uses it as t or t - 1
    eqs = run([[1, 2, 3, 4]], eq=[1, 0, 1, 1])
    np.testing.assert_array_equal(eqs.row, [3])
    np.testing.assert_array_equal(eqs.prev, [2])


def test_a_missing_value_removes_the_two_equations_that_touch_it():
    base = [[1, 2, 3, 4]]
    # y missing at t=2 removes (2,1) and (3,2); only (4,3) survives
    np.testing.assert_array_equal(run(base, y=[0, NAN, 2, 3]).row, [3])
    # q missing at t=3 removes (3,2) and (4,3); only (2,1) survives
    np.testing.assert_array_equal(run(base, q=[1, 1, NAN, 1]).row, [1])
    # a regressor missing at the last period removes only (4,3)
    np.testing.assert_array_equal(run(base, x=[1, 1, 1, NAN]).row, [1, 2])


def test_unit_without_consecutive_periods_has_no_equation():
    eqs = run([[1, 3, 5], [1, 2]])
    assert eqs.n_equations == 1
    assert eqs.n_active_units == 1
    np.testing.assert_array_equal(eqs.unit_ptr, [0, 0, 1])


def test_empty_input():
    eqs = fd_equations(
        np.zeros(1, np.int64), np.zeros(0, np.int64), np.zeros(0, bool),
        np.zeros(0), np.zeros(0), np.zeros((0, 1)),
    )  # fmt: skip
    assert eqs.n_equations == 0
    np.testing.assert_array_equal(eqs.pair_ptr, [0])
