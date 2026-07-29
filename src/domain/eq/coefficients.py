from dataclasses import dataclass


@dataclass(frozen=True)
class BiquadCoefficients:
    """Value object: biquad filter coefficients (float64)."""

    b0: float
    b1: float
    b2: float
    a1: float
    a2: float
