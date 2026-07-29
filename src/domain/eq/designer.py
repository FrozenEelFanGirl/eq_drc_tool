from dataclasses import dataclass
from typing import Protocol

from .coefficients import BiquadCoefficients
from .params import FilterParams
from .quantizer import QuantizedCoefficients


@dataclass(frozen=True)
class DesignedCoefficients:
    """Float biquad coefficients paired with their Q2.14 quantized form."""
    float_coeffs: BiquadCoefficients
    quantized: QuantizedCoefficients


class FilterDesigner(Protocol):
    """Port: given filter parameters, produce float + quantized coefficients."""

    def design(self, params: FilterParams, sample_rate: int) -> DesignedCoefficients: ...
