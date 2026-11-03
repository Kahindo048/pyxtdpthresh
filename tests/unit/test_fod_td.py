"""Forward orthogonal deviations and time-effect projections on hand-checkable panels."""

import numpy as np
import pytest
from scipy import sparse

from pyxtdpthresh.kernels.reference import transforms as ref_transforms
from pyxtdpthresh.kernels.transforms import fod_triplets
from pyxtdpthresh.transforms.fod import fod_equations
from pyxtdpthresh.transforms.td import fd_time_effects, fod_time_effects


def panel(times_by_unit):
    offsets = np.concatenate([[0], np.cumsum([len(t) for t in times_by_unit])]).astype(np.int64)
    return offsets, np.concatenate(times_by_unit).astype(np.int64)


def test_fod_of_three_rows_matches_the_formula():
    offsets, time = panel([[1, 2, 3]])
    y = np.array([1.0, 4.0, 10.0])
    n = 3
    eqs = fod_equations(offsets, time, np.ones(n, bool), y, np.ones(n), np.ones((n, 1)))
    assert eqs.row.tolist() == [0, 1] and eqs.time.tolist() == [1, 2]
    t = sparse.csr_matrix((eqs.pair_w, eqs.pair_lev, eqs.pair_ptr), shape=(2, 3))
    got = t @ y
    c1, c2 = np.sqrt(2 / 3), np.sqrt(1 / 2)
    np.testing.assert_allclose(got, [c1 * (1 - (4 + 10) / 2), c2 * (4 - 10)])


def test_fod_uses_later_equation_rows_whatever_their_dates():
    # history-only row 1 and a calendar gap: only the equation rows 0, 2, 3 count
    offsets, time = panel([[1, 2, 5, 6]])
    eq = np.array([True, False, True, True])
    n = 4
    eqs = fod_equations(offsets, time, eq, np.arange(4.0), np.ones(n), np.ones((n, 1)))
    assert eqs.row.tolist() == [0, 2]
    assert eqs.pair_lev.tolist() == [0, 2, 3, 2, 3]
    a, b = np.sqrt(2 / 3), np.sqrt(1 / 2)
    np.testing.assert_allclose(eqs.pair_w, [a, -a / 2, -a / 2, b, -b])


def test_units_with_fewer_than_two_equation_rows_have_no_equation():
    offsets, time = panel([[1], [1, 2], []])
    eqs = fod_equations(offsets, time, np.ones(3, bool), np.zeros(3), np.ones(3), np.ones((3, 1)))
    assert eqs.unit.tolist() == [1] and eqs.unit_ptr.tolist() == [0, 0, 1, 1]


@pytest.mark.parametrize("seed", range(5))
def test_fod_kernel_equals_the_reference(seed):
    rng = np.random.default_rng(seed)
    sizes = rng.integers(0, 8, size=10)
    offsets = np.concatenate([[0], np.cumsum(sizes)]).astype(np.int64)
    flag = rng.random(int(offsets[-1])) < 0.75
    for got, want in zip(fod_triplets(offsets, flag), ref_transforms.fod_triplets(offsets, flag),
                         strict=True):  # fmt: skip
        np.testing.assert_array_equal(got, want)


def test_period_demeaning_is_exact_and_drops_single_equation_periods():
    times = np.array([1, 1, 1, 2, 2, 3])
    part = fd_time_effects(times)
    assert part.keep.tolist() == [0, 1, 2, 3, 4]
    values = np.array([1.0, 2.0, 6.0, 10.0, 20.0, 7.0])
    np.testing.assert_allclose(part.apply(values), [-2, -1, 3, -5, 5, 0])
    matrix = np.column_stack([values, 2 * values])
    np.testing.assert_allclose(part.apply(matrix)[:, 1], 2 * part.apply(values))


def test_fod_projection_removes_the_transformed_period_dummies():
    offsets, time = panel([[1, 2, 3, 4], [1, 2, 3, 4], [2, 3, 4]])
    n = time.size
    eqs = fod_equations(offsets, time, np.ones(n, bool), np.zeros(n), np.ones(n), np.ones((n, 1)))
    t = sparse.csr_matrix((eqs.pair_w, eqs.pair_lev, eqs.pair_ptr), shape=(eqs.row.size, n))
    periods = np.unique(time)
    rank = np.searchsorted(periods, time)
    part = fod_time_effects(t, rank.astype(np.int64), periods.size)
    onehot = sparse.csr_matrix((np.ones(n), (np.arange(n), rank)), shape=(n, periods.size))
    dummies = np.asarray((t @ onehot).todense())
    # any combination of the transformed dummies is annihilated
    np.testing.assert_allclose(part.apply(dummies), 0.0, atol=1e-12)
    rng = np.random.default_rng(0)
    v = rng.normal(size=eqs.row.size)
    once = part.apply(v)
    np.testing.assert_allclose(part.apply(once), once, atol=1e-12)  # idempotent
    assert part.keep.size <= eqs.row.size
