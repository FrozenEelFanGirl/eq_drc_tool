from dataclasses import dataclass
from enum import IntEnum


class FilterType(IntEnum):
    BYPASS = 0
    PEAK = 1
    NOTCH = 2
    LOWSHELF = 3
    HIGHSHELF = 4
    HPF = 5
    LPF = 6


@dataclass(frozen=True)
class FilterParams:
    """Value object: user-facing parameters for one EQ band."""

    freq: float
    filter_type: FilterType
    gain_db: float
    Q: float
