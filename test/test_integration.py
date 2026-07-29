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

"""Layer 7: Full pipeline integration tests."""

from src.adapters.designers.interpolating import InterpolatingDesigner, load_coefficients
from src.adapters.scripts.bat_formatter import BatScriptFormatter
from src.application.drc_session import DRCSession
from src.application.eq_session import EQSession
from src.application.script_composer import ScriptComposer
from src.domain.eq.quantizer import quantize
from src.domain.script.register_map import REG16


class TestFullPipeline:
    @classmethod
    def setup_class(cls):
        load_coefficients()

    def test_bypass_48k_bat_generation(self):
        designer = InterpolatingDesigner()
        eq = EQSession()
        drc = DRCSession()
        composer = ScriptComposer(designer)
        formatter = BatScriptFormatter()

        writes = composer.compose(eq, drc)
        bat = formatter.format(writes)

        assert "@echo off" in bat
        assert "pause" in bat
        assert "0x00002066" in bat  # REG16
        assert "0x00002065" in bat  # REG15
        # Verify the 7 frequency labels are present in coefficient addressing
        for addr in range(0x30, 0x45):
            assert f"0x{addr:02X}" in bat, f"Missing address 0x{addr:02X}"

    def test_drc_off_no_drc_writes(self):
        designer = InterpolatingDesigner()
        eq = EQSession()
        drc = DRCSession()
        drc.disable()
        composer = ScriptComposer(designer)

        writes = composer.compose(eq, drc)
        # Last write should be REG16=0x00 (DRC disable)
        assert writes[-1].address == REG16 and writes[-1].value == 0x00

    def test_bypass_coefficients_applied(self):
        designer = InterpolatingDesigner()
        eq = EQSession()
        drc = DRCSession()
        composer = ScriptComposer(designer)

        writes = composer.compose(eq, drc)
        # Find all REG10 writes that should be 0x40 (b0 MSB of bypass coeff)
        bypass_b0_writes = [
            rw for rw in writes
            if rw.address == 0x2060 and rw.value == 0x40
        ]
        # Should have 7 bands × 1 (only B=0 group has b0 in upper byte)
        assert len(bypass_b0_writes) == 7

    def test_all_bypass_quantized(self):
        from src.domain.eq.coefficients import BiquadCoefficients

        coeffs = BiquadCoefficients(b0=1.0, b1=0.0, b2=0.0, a1=0.0, a2=0.0)
        q = quantize(coeffs)

        assert q.b0_b2 == 0x40000000
        assert q.b1_na2 == 0x00000000
        assert q.na1_unused == 0x00000000

    def test_export_contains_all_registers(self):
        designer = InterpolatingDesigner()
        eq = EQSession()
        drc = DRCSession()
        composer = ScriptComposer(designer)
        formatter = BatScriptFormatter()

        writes = composer.compose(eq, drc)
        bat = formatter.format(writes)

        for addr in [0x2060, 0x2061, 0x2062, 0x2063, 0x2064, 0x2065, 0x2066]:
            assert f"0x{addr:08X}" in bat, f"Missing register 0x{addr:08X}"
