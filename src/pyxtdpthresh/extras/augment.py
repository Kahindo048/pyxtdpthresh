"""Add the series of a fit (residuals, fitted values, regime) to a DataFrame (layer 6).

``augment(fit, frame)`` is ``predict`` for a whole table: it returns a copy of the data the model
was estimated on with one column per series, aligned row by row and missing where a series is not
defined (the first period of a unit, a row outside the estimation sample).  It reads the fit and
never estimates.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING

import pandas as pd

from pyxtdpthresh._errors import SpecificationError
from pyxtdpthresh._i18n import message
from pyxtdpthresh.models.xtdpthresh.predict import KINDS

if TYPE_CHECKING:
    from pyxtdpthresh.models.xtdpthresh.fit import PointFit

#: The series added when none is asked for.
DEFAULT_KINDS: tuple[str, ...] = ("residuals", "xb", "regime")


def augment(
    fit: PointFit,
    frame: pd.DataFrame,
    *,
    kinds: Sequence[str] = DEFAULT_KINDS,
    prefix: str = "",
    overwrite: bool = False,
) -> pd.DataFrame:
    """Return a copy of ``frame`` with the series of ``fit`` added as columns.

    Parameters
    ----------
    fit
        Result of an ``xtdpthresh`` estimation.
    frame
        The data the model was estimated on (same keys); it is not modified.
    kinds
        Series to add among ``"residuals"``, ``"xb"`` (the fit of the transformed equation),
        ``"ar_residuals"`` and ``"regime"`` (``1`` above the threshold, ``0`` below, missing
        where the threshold variable is).  The column of each has the name of its series.
    prefix
        Text put before the column names (``prefix="m1_"`` gives ``m1_residuals``).
    overwrite
        Replace a column that already has the name of a series; by default that is an error.

    Returns
    -------
    pandas.DataFrame
        ``frame`` and the new columns.

    Raises
    ------
    SpecificationError
        A series name is not known (``predict_kind``), or a column already exists
        (``augment_exists``).
    """
    wanted = [kinds] if isinstance(kinds, str) else list(kinds)
    for kind in wanted:
        if kind not in KINDS:
            raise SpecificationError(
                message("predict_kind", kind=kind, options=", ".join(KINDS)),
                stata_code=198,
                key="predict_kind",
            )
    clashes = [prefix + kind for kind in wanted if prefix + kind in frame.columns]
    if clashes and not overwrite:
        raise SpecificationError(
            message("augment_exists", columns=", ".join(clashes)), key="augment_exists"
        )
    out = frame.copy()
    for kind in wanted:
        out[prefix + kind] = fit.predict(kind, frame)
    return out
