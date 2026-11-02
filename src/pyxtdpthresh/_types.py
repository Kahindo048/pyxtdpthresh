"""Type aliases shared by the whole package (layer 0)."""

from __future__ import annotations

from typing import Literal

import numpy as np
import numpy.typing as npt

FloatArray = npt.NDArray[np.float64]
IntArray = npt.NDArray[np.int64]
BoolArray = npt.NDArray[np.bool_]
UIntArray = npt.NDArray[np.uint64]

#: Transformation that removes the unit effect.
Method = Literal["fd", "fod"]
#: Language of messages and diagnostic reports.
Lang = Literal["en", "fr"]
#: Bootstrap scheme of the threshold confidence set.
BootType = Literal["wild", "unit"]
#: Placement of the threshold grid points.
GridType = Literal["uniform", "quantile"]
