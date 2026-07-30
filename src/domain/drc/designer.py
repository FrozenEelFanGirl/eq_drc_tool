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
from typing import Protocol

from .params import DRCParams


@dataclass(frozen=True)
class DrcRegisters:
    """Register values for REG17–REG27 from a DRC parameter set."""

    threshold_msb: int  # REG17
    threshold_lsb: int  # REG18
    update_window: int  # REG19
    attack_coe_msb: int  # REG20
    release_coe_msb: int  # REG21
    ratio_mixed: int  # REG22
    gain_margin: int  # REG23
    noise_gate: int  # REG24
    timeout_gain_balance: int  # REG25
    makeup_gain: int  # REG26
    max_output: int  # REG27


class DRCDesigner(Protocol):
    """Port: given DRC parameters, produce register values."""

    def design(self, params: DRCParams) -> DrcRegisters: ...
