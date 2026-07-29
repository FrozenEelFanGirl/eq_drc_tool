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

from ..domain.eq.coefficients import BiquadCoefficients
from ..domain.eq.designer import DesignedCoefficients, FilterDesigner
from ..domain.eq.params import FilterParams, FilterType
from ..domain.eq.quantizer import quantize
from .ports import Observer

BANDS = 7
_BYPASS_FLOAT = BiquadCoefficients(b0=1.0, b1=0.0, b2=0.0, a1=0.0, a2=0.0)
BYPASS_COEFFS = DesignedCoefficients(float_coeffs=_BYPASS_FLOAT, quantized=quantize(_BYPASS_FLOAT))


class EQSession:
    """Observable state for 7 EQ bands."""

    def __init__(self, designer: FilterDesigner) -> None:
        self._designer = designer
        self.sample_rate: int = 48000
        self.bands: list[FilterParams | None] = [None] * BANDS
        self.bypass_flags: list[bool] = [True] * BANDS
        self._observers: list[Observer] = []

    # --- Observer ---
    def attach(self, observer: Observer) -> None:
        self._observers.append(observer)

    def detach(self, observer: Observer) -> None:
        self._observers.remove(observer)

    def _notify(self) -> None:
        for obs in self._observers:
            obs.on_state_changed()

    # --- Mutators ---
    def set_sample_rate(self, rate: int) -> None:
        self.sample_rate = rate
        self._notify()

    def update_band(self, index: int, params: FilterParams) -> None:
        self.bands[index] = params
        self.bypass_flags[index] = False
        self._notify()

    def toggle_band(self, index: int) -> None:
        self.bypass_flags[index] = not self.bypass_flags[index]
        self._notify()

    def set_all_bypass(self) -> None:
        for i in range(BANDS):
            self.bypass_flags[i] = True
        self._notify()

    # --- Queries ---
    def active_params(self) -> list[FilterParams | None]:
        """Return params for non-bypassed bands, None for bypassed."""
        return [
            p if not self.bypass_flags[i] else None
            for i, p in enumerate(self.bands)
        ]

    def active_coeffs(self) -> list[DesignedCoefficients]:
        """Compute coefficients for all 7 bands (bypassed → identity)."""
        coeffs: list[DesignedCoefficients] = []
        for i in range(BANDS):
            if self.bypass_flags[i] or self.bands[i] is None:
                coeffs.append(BYPASS_COEFFS)
            else:
                coeffs.append(self._designer.design(self.bands[i], self.sample_rate))
        return coeffs
