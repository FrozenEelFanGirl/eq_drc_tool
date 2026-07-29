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

"""Hardware DRC designer: converts DRCParams → DrcRegisters."""

from ...domain.drc.designer import DRCDesigner, DrcRegisters
from ...domain.drc.params import DRCParams


class HardwareDrcDesigner:
    """Maps DRCParams (register-level values) to DrcRegisters."""

    def design(self, params: DRCParams) -> DrcRegisters:
        # Threshold
        thr_raw = int(0x58FA + params.threshold_db * 256)
        thr_raw = max(0, min(0xFFFF, thr_raw))

        # Ratio + attack/release LSBs: REG22
        ratio_mixed = (params.ratio_idx << 5) | ((params.attack_val & 3) << 2) | (params.release_val & 3)

        # Noise gate: dB → val
        ng_val = max(0, min(255, round((params.noise_gate_db * 256 + 0x58FA) / 32)))

        # Makeup gain: dB → val
        mu_val = max(0, min(255, round(params.makeup_gain_db * 8)))

        # Max output: dB → val
        # dB = val - 88.98, so val = round(dB + 89)
        mo_val = max(0, min(255, round(params.max_output_db + 89)))

        # Timeout fixed to 0, balance in low 2 bits
        timeout_balance = params.gain_balance & 3

        return DrcRegisters(
            threshold_msb=(thr_raw >> 8) & 0xFF,
            threshold_lsb=thr_raw & 0xFF,
            update_window=params.update_window,
            attack_coe_msb=(params.attack_val >> 2) & 0xFF,
            release_coe_msb=(params.release_val >> 2) & 0xFF,
            ratio_mixed=ratio_mixed,
            gain_compute=params.gain_compute,
            noise_gate=ng_val,
            timeout_gain_balance=timeout_balance,
            makeup_gain=mu_val,
            max_output=mo_val,
        )
