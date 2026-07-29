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

from ...domain.eq.coefficients import BiquadCoefficients
from ...domain.eq.designer import DesignedCoefficients
from ...domain.eq.params import FilterParams, FilterType
from ...domain.eq.quantizer import quantize


class RBJDesigner:
    """RBJ Audio EQ Cookbook biquad coefficient designer."""

    def design(self, params: FilterParams, sample_rate: int) -> DesignedCoefficients:
        if params.filter_type == FilterType.BYPASS:
            fc = BiquadCoefficients(b0=1.0, b1=0.0, b2=0.0, a1=0.0, a2=0.0)
        elif params.filter_type in (FilterType.HPF, FilterType.LPF):
            fc = self._design_edge(params, sample_rate)
        else:
            fc = self._design_rbj(params, sample_rate)
        return DesignedCoefficients(float_coeffs=fc, quantized=quantize(fc))

    def _design_edge(self, params: FilterParams,
                     sample_rate: int) -> BiquadCoefficients:
        """Design HPF or LPF using RBJ cookbook formulas."""
        w0 = 2.0 * np.pi * params.freq / sample_rate
        cos_w = np.cos(w0)
        sin_w = np.sin(w0)
        alpha = sin_w / (2.0 * max(params.Q, 0.1))
        a0 = 1.0 + alpha

        if params.filter_type == FilterType.HPF:
            b0 = (1.0 + cos_w) / 2.0 / a0
            b1 = -(1.0 + cos_w) / a0
            b2 = (1.0 + cos_w) / 2.0 / a0
        else:  # LPF
            b0 = (1.0 - cos_w) / 2.0 / a0
            b1 = (1.0 - cos_w) / a0
            b2 = (1.0 - cos_w) / 2.0 / a0

        a1 = -2.0 * cos_w / a0
        a2 = (1.0 - alpha) / a0

        return BiquadCoefficients(b0=float(b0), b1=float(b1), b2=float(b2),
                                   a1=float(a1), a2=float(a2))

    def _design_rbj(self, params: FilterParams,
                    sample_rate: int) -> BiquadCoefficients:
        """Design peaking/notch/shelving using RBJ formulas."""
        w0 = 2.0 * np.pi * params.freq / sample_rate
        cos_w = np.cos(w0)
        sin_w = np.sin(w0)
        A = 10.0 ** (params.gain_db / 40.0)

        if params.filter_type == FilterType.PEAK:
            alpha = sin_w / (2.0 * max(params.Q, 0.1))
            a0 = 1.0 + alpha / A
            b0 = (1.0 + alpha * A) / a0
            b1 = (-2.0 * cos_w) / a0
            b2 = (1.0 - alpha * A) / a0
            a1 = (-2.0 * cos_w) / a0
            a2 = (1.0 - alpha / A) / a0

        elif params.filter_type == FilterType.NOTCH:
            alpha = sin_w / (2.0 * max(params.Q, 0.1))
            a0 = 1.0 + alpha
            b0 = 1.0 / a0
            b1 = (-2.0 * cos_w) / a0
            b2 = 1.0 / a0
            a1 = (-2.0 * cos_w) / a0
            a2 = (1.0 - alpha) / a0

        elif params.filter_type == FilterType.LOWSHELF:
            alpha = sin_w / 2.0 * np.sqrt(
                (A + 1.0 / A) * (1.0 / max(params.Q, 0.1) - 1.0) + 2.0
            )
            a0 = (A + 1.0) + (A - 1.0) * cos_w + 2.0 * np.sqrt(A) * alpha
            b0 = A * ((A + 1.0) - (A - 1.0) * cos_w + 2.0 * np.sqrt(A) * alpha) / a0
            b1 = 2.0 * A * ((A - 1.0) - (A + 1.0) * cos_w) / a0
            b2 = A * ((A + 1.0) - (A - 1.0) * cos_w - 2.0 * np.sqrt(A) * alpha) / a0
            a1 = -2.0 * ((A - 1.0) + (A + 1.0) * cos_w) / a0
            a2 = ((A + 1.0) + (A - 1.0) * cos_w - 2.0 * np.sqrt(A) * alpha) / a0

        elif params.filter_type == FilterType.HIGHSHELF:
            alpha = sin_w / 2.0 * np.sqrt(
                (A + 1.0 / A) * (1.0 / max(params.Q, 0.1) - 1.0) + 2.0
            )
            a0 = (A + 1.0) - (A - 1.0) * cos_w + 2.0 * np.sqrt(A) * alpha
            b0 = A * ((A + 1.0) + (A - 1.0) * cos_w + 2.0 * np.sqrt(A) * alpha) / a0
            b1 = -2.0 * A * ((A - 1.0) + (A + 1.0) * cos_w) / a0
            b2 = A * ((A + 1.0) + (A - 1.0) * cos_w - 2.0 * np.sqrt(A) * alpha) / a0
            a1 = 2.0 * ((A - 1.0) - (A + 1.0) * cos_w) / a0
            a2 = ((A + 1.0) - (A - 1.0) * cos_w - 2.0 * np.sqrt(A) * alpha) / a0

        else:
            return BiquadCoefficients(b0=1.0, b1=0.0, b2=0.0, a1=0.0, a2=0.0)

        return BiquadCoefficients(b0=float(b0), b1=float(b1), b2=float(b2),
                                   a1=float(a1), a2=float(a2))
