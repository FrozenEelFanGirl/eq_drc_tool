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

from ..domain.drc.designer import DRCDesigner
from ..domain.eq.designer import FilterDesigner
from ..domain.script.commands import RegisterWrite
from ..domain.script.register_map import (
    BANDS_COUNT,
    COMPLETION_ADDR,
    DRC_PARAM_REGISTERS,
    REG10,
    REG11,
    REG12,
    REG13,
    REG14,
    REG15,
    REG16,
    DrcCommand,
    EqCommand,
    eq_addr,
)
from .drc_session import DRCSession
from .eq_session import EQSession


class ScriptComposer:
    """Compose EQSession + DRCSession → list[RegisterWrite]."""

    def __init__(self, eq_designer: FilterDesigner,
                 drc_designer: DRCDesigner | None = None) -> None:
        self.eq_designer = eq_designer
        self._drc_designer = drc_designer

    def compose(self, eq_session: EQSession, drc_session: DRCSession,
                reset_coe: bool = False) -> list[RegisterWrite]:
        w: list[RegisterWrite] = []

        # 1. Force clock
        w.append(RegisterWrite(REG16, 0x10))

        # 2. Reset → IDLE → WAIT
        cmd = EqCommand.RESET_DATA_COE if reset_coe else EqCommand.RESET_DATA
        w.append(RegisterWrite(REG15, cmd.value))

        # 3. Enter CONFIG (×2)
        w.append(RegisterWrite(REG15, EqCommand.ENTER_CONFIG.value))
        w.append(RegisterWrite(REG15, EqCommand.ENTER_CONFIG.value))

        # 4. Clear coefficient + address registers
        for reg in (REG10, REG11, REG12, REG13, REG14):
            w.append(RegisterWrite(reg, 0x00))

        # 5. Write 21 coefficient groups (7 bands × 3 groups)
        coeffs = eq_session.active_coeffs()
        rate = eq_session.sample_rate

        for stage in range(BANDS_COUNT):
            q = coeffs[stage].quantized
            words = [q.b0_b2, q.b1_na2, q.na1_unused]

            for group_idx, word in enumerate(words):
                addr = eq_addr(rate, stage, group_idx)
                w.append(RegisterWrite(REG10, (word >> 24) & 0xFF))
                w.append(RegisterWrite(REG11, (word >> 16) & 0xFF))
                w.append(RegisterWrite(REG12, (word >> 8) & 0xFF))
                w.append(RegisterWrite(REG13, word & 0xFF))
                w.append(RegisterWrite(REG14, addr))
                w.append(RegisterWrite(REG15, EqCommand.WRITE_PULSE.value))

        # 6. Completion → exits CONFIG → WAIT → RUNNING
        w.append(RegisterWrite(REG14, COMPLETION_ADDR))
        w.append(RegisterWrite(REG15, EqCommand.WRITE_PULSE.value))

        # 7. DRC config
        if drc_session.enabled and self._drc_designer:
            drc_regs = self._drc_designer.design(drc_session.params)
            w.append(RegisterWrite(REG16, DrcCommand.CLOCK_FORCE_NO_DRC.value))
            w.extend(_drc_reg_writes(drc_regs))
            w.append(RegisterWrite(REG16, DrcCommand.ENABLE.value))
        else:
            w.append(RegisterWrite(REG16, DrcCommand.DISABLE.value))

        return w


def _drc_reg_writes(drc) -> list[RegisterWrite]:
    from ..domain.drc.designer import DrcRegisters
    return [
        RegisterWrite(DRC_PARAM_REGISTERS[0], drc.threshold_msb),
        RegisterWrite(DRC_PARAM_REGISTERS[1], drc.threshold_lsb),
        RegisterWrite(DRC_PARAM_REGISTERS[2], drc.update_window),
        RegisterWrite(DRC_PARAM_REGISTERS[3], drc.attack_coe_msb),
        RegisterWrite(DRC_PARAM_REGISTERS[4], drc.release_coe_msb),
        RegisterWrite(DRC_PARAM_REGISTERS[5], drc.ratio_mixed),
        RegisterWrite(DRC_PARAM_REGISTERS[6], drc.gain_margin),
        RegisterWrite(DRC_PARAM_REGISTERS[7], drc.noise_gate),
        RegisterWrite(DRC_PARAM_REGISTERS[8], drc.timeout_gain_balance),
        RegisterWrite(DRC_PARAM_REGISTERS[9], drc.makeup_gain),
        RegisterWrite(DRC_PARAM_REGISTERS[10], drc.max_output),
    ]
