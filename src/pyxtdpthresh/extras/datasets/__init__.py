"""Bundled datasets: ``load_dataset("invest")`` and ``list_datasets()`` (layer 6)."""

from __future__ import annotations

from dataclasses import dataclass
from importlib import resources

import pandas as pd

from pyxtdpthresh._errors import SpecificationError
from pyxtdpthresh._i18n import message


@dataclass(frozen=True)
class Dataset:
    """A bundled dataset: its file, its panel structure and its documentation."""

    file: str
    id: str
    time: str
    description: str
    labels: dict[str, str]


DATASETS: dict[str, Dataset] = {
    "invest": Dataset(
        file="invest.csv",
        id="firm",
        time="year",
        description=(
            "Hansen (1999, Journal of Econometrics) firm investment panel: 565 firms x 15 years, "
            "1973-1987, balanced. Used in the worked examples of xtdpthresh (Nguyen and Lai 2026)."
        ),
        labels={
            "firm": "Firm identifier (arbitrary integer, not CUSIP)",
            "year": "Calendar year (1973-1987)",
            "invest": "Investment / beginning-of-period capital (I/K)",
            "tobin_q": "Tobin's Q (market value / book value)",
            "cashflow": "Cash flow / beginning-of-period capital (CF/K)",
            "debt": "Long-term debt / total assets (leverage; threshold var)",
        },
    ),
}


def list_datasets() -> dict[str, str]:
    """Return the bundled datasets and their descriptions.

    Returns
    -------
    dict
        ``{name: description}``; the names are those :func:`load_dataset` accepts.

    Examples
    --------
    >>> import pyxtdpthresh as pyx
    >>> list(pyx.list_datasets())
    ['invest']
    """
    return {name: data.description for name, data in DATASETS.items()}


def load_dataset(name: str = "invest") -> pd.DataFrame:
    """Load a bundled dataset as a long DataFrame.

    Parameters
    ----------
    name
        One of :func:`list_datasets` (default ``"invest"``, Hansen's investment panel).

    Returns
    -------
    pandas.DataFrame
        One row per (unit, period).  ``attrs`` holds ``id`` and ``time`` (the panel variables to
        pass as ``id=`` and ``time=``), ``description`` and ``variable_labels``.

    Raises
    ------
    SpecificationError
        ``name`` is not a bundled dataset (``key`` is ``dataset_unknown``).

    Examples
    --------
    >>> import pyxtdpthresh as pyx
    >>> df = pyx.load_dataset("invest")
    >>> df.shape[0], df["firm"].nunique()
    (8475, 565)
    """
    if name not in DATASETS:
        raise SpecificationError(
            message("dataset_unknown", name=name, options=", ".join(DATASETS)),
            key="dataset_unknown",
        )
    data = DATASETS[name]
    path = resources.files("pyxtdpthresh.extras.datasets").joinpath(data.file)
    with resources.as_file(path) as file:
        frame = pd.read_csv(file)
    frame.attrs.update(
        id=data.id, time=data.time, description=data.description, variable_labels=dict(data.labels)
    )
    return frame


__all__ = ["DATASETS", "Dataset", "list_datasets", "load_dataset"]
