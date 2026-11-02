"""Sample selection: Stata's ``if`` / ``in`` and ``marksample`` / ``markout``."""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np
import pandas as pd

from pyxtdpthresh._errors import DataError
from pyxtdpthresh._i18n import message
from pyxtdpthresh._types import BoolArray, FloatArray


def resolve_where(frame: pd.DataFrame, where: str | Sequence[bool] | BoolArray | None) -> BoolArray:
    """Turn the ``where`` argument into a boolean mask over the rows of ``frame``.

    Parameters
    ----------
    frame
        Input data.
    where
        ``None`` keeps every row; a boolean array or Series (aligned by position); or a string
        expression evaluated with :meth:`pandas.DataFrame.eval`, the counterpart of Stata's
        ``if``.  A missing value in the condition counts as False, whereas Stata counts it
        as true; ``xtdpthresh`` removes such rows afterwards through the missing-value
        check of the variables involved.

    Raises
    ------
    DataError
        If ``where`` is not boolean or has the wrong length.
    """
    n = len(frame)
    if where is None:
        return np.ones(n, dtype=np.bool_)
    result = frame.eval(where) if isinstance(where, str) else where
    mask = np.asarray(result)
    if mask.dtype == object:
        mask = pd.array(mask, dtype="boolean").fillna(False).to_numpy(dtype=bool)
    if mask.dtype.kind != "b" or mask.shape != (n,):
        raise DataError(message("where_not_boolean", n=n, got=f"{mask.dtype} {mask.shape}"))
    return np.asarray(mask, dtype=np.bool_)


def complete_rows(values: FloatArray) -> BoolArray:
    """Rows of a 2-D array in which every entry is finite (Stata ``markout``)."""
    arr = np.asarray(values, dtype=np.float64)
    if arr.ndim == 1:
        arr = arr[:, None]
    return np.asarray(np.isfinite(arr).all(axis=1), dtype=np.bool_)
