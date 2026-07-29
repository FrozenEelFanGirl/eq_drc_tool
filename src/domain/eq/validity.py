import numpy as np

from .coefficients import BiquadCoefficients
from .quantizer import Q_MAX, Q_MIN


def check(coeffs: BiquadCoefficients) -> tuple[bool, str | None]:
    """Check whether biquad coefficients are valid for Q2.14 quantization.

    Returns (is_valid, error_message).
    """
    values = {
        "b0": coeffs.b0, "b1": coeffs.b1, "b2": coeffs.b2,
        "a1": coeffs.a1, "a2": coeffs.a2,
    }
    for name, v in values.items():
        if np.isnan(v) or np.isinf(v):
            return False, f"{name}={v} (non-finite)"
        if v < Q_MIN:
            return False, f"{name}={v:.6f} < Q2.14 min ({Q_MIN})"
        if v >= Q_MAX:
            return False, f"{name}={v:.6f} >= Q2.14 max ({Q_MAX:.6f})"
    return True, None
