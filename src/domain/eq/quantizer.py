from dataclasses import dataclass

from .coefficients import BiquadCoefficients

Q_SCALE = 1 << 14  # 16384
Q_MAX = 2.0 - 1.0 / Q_SCALE
Q_MIN = -2.0


@dataclass(frozen=True)
class QuantizedCoefficients:
    """Three 32-bit packed words: B0 (b0/b2), B1 (b1/na2), B2 (na1/unused)."""

    b0_b2: int  # upper 16: b0, lower 16: b2
    b1_na2: int  # upper 16: b1, lower 16: na2 = -a2
    na1_unused: int  # upper 16: na1 = -a1, lower 16: unused


def _quantize(value: float) -> int:
    """Convert float to Q2.14 16-bit integer."""
    clamped = max(Q_MIN, min(Q_MAX, value))
    return int(round(clamped * Q_SCALE)) & 0xFFFF


def _pack(high: int, low: int) -> int:
    return (high << 16) | (low & 0xFFFF)


def dequantize(value: int) -> float:
    """Convert Q2.14 16-bit unsigned integer to signed float."""
    sv = value - 0x10000 if value >= 0x8000 else value
    return sv / Q_SCALE


def unpack_to_coeffs(q: QuantizedCoefficients) -> BiquadCoefficients:
    """Convert packed Q2.14 coefficients back to float BiquadCoefficients."""
    b0 = dequantize((q.b0_b2 >> 16) & 0xFFFF)
    b2 = dequantize(q.b0_b2 & 0xFFFF)
    b1 = dequantize((q.b1_na2 >> 16) & 0xFFFF)
    na2 = dequantize(q.b1_na2 & 0xFFFF)
    na1 = dequantize((q.na1_unused >> 16) & 0xFFFF)
    return BiquadCoefficients(b0=b0, b1=b1, b2=b2, a1=-na1, a2=-na2)


def quantize(coeffs: BiquadCoefficients) -> QuantizedCoefficients:
    """Convert biquad coefficients to Q2.14 packed register words.

    Uses negated feedback convention: na1 = -a1, na2 = -a2.
    B=2 lower 16 bits are unused placeholder.
    """
    b0 = _quantize(coeffs.b0)
    b1 = _quantize(coeffs.b1)
    b2 = _quantize(coeffs.b2)
    na1 = _quantize(-coeffs.a1)
    na2 = _quantize(-coeffs.a2)

    return QuantizedCoefficients(
        b0_b2=_pack(b0, b2),
        b1_na2=_pack(b1, na2),
        na1_unused=_pack(na1, 0),
    )
