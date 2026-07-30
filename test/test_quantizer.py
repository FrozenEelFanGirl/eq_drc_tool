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

"""Layer 2: Float coefficients → Q2.14 packed words."""

from src.domain.eq.coefficients import BiquadCoefficients
from src.domain.eq.quantizer import _pack, _quantize, quantize


class TestQuantize:
    def test_bypass_b0(self):
        assert _quantize(1.0) == 0x4000

    def test_bypass_zeros(self):
        assert _quantize(0.0) == 0x0000

    def test_bypass_b0_b2(self):
        q = quantize(BiquadCoefficients(b0=1.0, b1=0.0, b2=0.0, a1=0.0, a2=0.0))
        assert q.b0_b2 == _pack(0x4000, 0x0000) == 0x40000000

    def test_bypass_b1_na2(self):
        q = quantize(BiquadCoefficients(b0=1.0, b1=0.0, b2=0.0, a1=0.0, a2=0.0))
        assert q.b1_na2 == _pack(0x0000, 0x0000) == 0x00000000

    def test_negated_a1(self):
        # na1 = -a1, stored in upper 16 bits of B=2
        q = quantize(BiquadCoefficients(b0=1.0, b1=0.0, b2=0.0, a1=-0.5, a2=0.0))
        na1 = (q.na1_unused >> 16) & 0xFFFF
        # a1 = -0.5 → na1 = -(-0.5) = 0.5 → Q2.14 = 0x2000
        assert na1 == 0x2000

    def test_negated_a2(self):
        # na2 = -a2, stored in lower 16 bits of B=1
        q = quantize(BiquadCoefficients(b0=1.0, b1=0.0, b2=0.0, a1=0.0, a2=0.25))
        na2 = q.b1_na2 & 0xFFFF
        # a2 = 0.25 → na2 = -0.25 → Q2.14 = 0xF000 (signed -16384*0.25 = -4096 = 0xF000)
        assert na2 == 0xF000

    def test_range_clamp_positive(self):
        assert _quantize(3.0) == 0x7FFF  # max positive

    def test_range_clamp_negative(self):
        assert _quantize(-2.0) == 0x8000  # max negative

    def test_pack(self):
        assert _pack(0x4053, 0x3F05) == 0x40533F05


# (sample_rate, freq_hz, Q) → (b0_b2, b1_na2, na1_unused)
GOLDEN_PEAK = {
    (48000, 1000, 9): (0x40533F05, 0x81BEC0A7, 0x7E420000),
    (48000, 4000, 15): (0x40BE3DC4, 0x9271C17E, 0x6D8F0000),
    (48000, 7000, 25): (0x40B53DDF, 0xB2F2C16C, 0x4D0E0000),
    (48000, 10000, 25): (0x40DC3D6A, 0xDF51C1BA, 0x20AF0000),
    (48000, 13000, 25): (0x40E23D59, 0x107AC1C6, 0xEF860000),
    (48000, 16000, 25): (0x40C63DAE, 0x3F3AC18D, 0xC0C60000),
    (48000, 19000, 15): (0x40E73D49, 0x641CC1D0, 0x9BE40000),
    (96000, 1000, 9): (0x402A3F82, 0x809AC054, 0x7F660000),
    (96000, 4000, 15): (0x40633ED6, 0x851DC0C7, 0x7AE30000),
    (96000, 7000, 25): (0x40653ECF, 0x8DEAC0CC, 0x72160000),
    (96000, 10000, 25): (0x408B3E5D, 0x9B52C118, 0x64AE0000),
    (96000, 13000, 25): (0x40AC3DFB, 0xAC7EC159, 0x53820000),
    (96000, 16000, 25): (0x40C63DAE, 0xC0C6C18D, 0x3F3A0000),
    (96000, 19000, 15): (0x41643BCF, 0xD7C1C2CC, 0x283F0000),
    (192000, 1000, 9): (0x40153FC1, 0x803CC02A, 0x7FC40000),
    (192000, 4000, 15): (0x40323F69, 0x817CC065, 0x7E840000),
    (192000, 7000, 25): (0x40343F63, 0x83BEC069, 0x7C420000),
    (192000, 10000, 25): (0x404A3F22, 0x8758C094, 0x78A80000),
    (192000, 13000, 25): (0x405F3EE3, 0x8C16C0BE, 0x73EA0000),
    (192000, 16000, 25): (0x40733EA7, 0x91EEC0E6, 0x6E120000),
    (192000, 19000, 15): (0x40DD3D67, 0x995EC1BC, 0x66A20000),
}


class TestRbjAgainstGolden:
    """Validate RBJDesigner output against known-good packed coefficients."""

    def test_bypass_all(self):
        from src.adapters.designers.rbj import RBJDesigner
        from src.domain.eq.params import FilterParams, FilterType

        designer = RBJDesigner()
        rates = [48000, 96000, 192000]
        freqs = [1000, 4000, 7000, 10000, 13000, 16000, 19000]
        for rate in rates:
            for freq in freqs:
                params = FilterParams(
                    freq=float(freq), filter_type=FilterType.BYPASS,
                    gain_db=0.0, Q=1.0,
                )
                result = designer.design(params, rate)
                q = result.quantized
                assert q.b0_b2 == 0x40000000
                assert q.b1_na2 == 0x00000000
                assert q.na1_unused == 0x00000000

    def test_peak_all(self):
        from src.adapters.designers.rbj import RBJDesigner
        from src.domain.eq.params import FilterParams, FilterType

        designer = RBJDesigner()
        for (rate, freq, Q), (exp_b0, exp_b1, exp_b2) in GOLDEN_PEAK.items():
            params = FilterParams(
                freq=float(freq), filter_type=FilterType.PEAK,
                gain_db=6.0, Q=float(Q),
            )
            result = designer.design(params, rate)
            q = result.quantized
            assert q.b0_b2 == exp_b0, f"fs={rate} f={freq} Q={Q}: b0_b2 mismatch"
            assert q.b1_na2 == exp_b1, f"fs={rate} f={freq} Q={Q}: b1_na2 mismatch"
            assert q.na1_unused == exp_b2, f"fs={rate} f={freq} Q={Q}: na1_unused mismatch"
