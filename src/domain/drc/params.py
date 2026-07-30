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

from dataclasses import dataclass


@dataclass(frozen=True)
class DRCParams:
    """DRC hardware register parameters (mutable for GUI binding)."""

    threshold_db: float = -24.0       # REG17/18: 1.7.8 signed, [-80, 0] dB
    ratio_idx: int = 4                # REG22[7:5]: 0=∞, 1=0.125, ..., 7=0.875
    attack_val: int = 0               # REG20+22[3:2]: 10-bit [0, 1023]
    release_val: int = 0              # REG21+22[1:0]: 10-bit [0, 1023]
    update_window: int = 96           # REG19: [0, 255], ≥96 recommended
    gain_margin_db: float = 0.258     # REG23: Q8.8, val = round(dB * 256)
    noise_gate_db: float = -69.977    # REG24: val [0,255], dB [-88.98, -57.10]
    gain_balance: int = 0             # REG25[1:0]: 0=indep, 1=L, 2=R, 3=max
    makeup_gain_db: float = 0.0       # REG26: absolute dB [0, 31.875]
    max_output_db: float = 0.02       # REG27: dB [-88.98, +166.02]
    extended_window: bool = False     # allow update_window < 96

    @property
    def ratio(self) -> float:
        """Compression slope (hardware ratio)."""
        return [float('inf'), 0.125, 0.25, 0.375, 0.5, 0.625, 0.75, 0.875][self.ratio_idx]
