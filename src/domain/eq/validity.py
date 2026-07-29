# Copyright (c) 2026 FrozenEelFanGirl & Senary
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

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
