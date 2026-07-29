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


class TestGoldenCoefficients:
    """Validate all 105 entries from coe_array.txt round-trip correctly."""

    def test_all_entries(self, coe_entries):
        from src.adapters.designers.interpolating import (
            InterpolatingDesigner,
            load_coefficients,
        )
        from src.domain.eq.params import FilterParams, FilterType

        load_coefficients()
        designer = InterpolatingDesigner()

        # Group by (rate, freq, type) → verify each
        seen = set()
        for entry in coe_entries:
            key = (entry["rate"], entry["freq"], entry["ftype"])
            if key in seen:
                continue
            seen.add(key)

            params = FilterParams(
                freq=float(entry["freq"]),
                filter_type=FilterType(entry["ftype"]),
                gain_db=6.0,
                Q=1.0,
            )
            coeffs = designer.design(params, entry["rate"])
            q = quantize(coeffs)

            # Find expected values for this key
            expected = {}
            for e in coe_entries:
                if (e["rate"], e["freq"], e["ftype"]) == key:
                    expected[e["bgroup"]] = e["packed32"]

            assert q.b0_b2 == expected[0], (
                f"Mismatch B=0: rate={key[0]}, freq={key[1]}, type={key[2]}"
            )
            assert q.b1_na2 == expected[1], (
                f"Mismatch B=1: rate={key[0]}, freq={key[1]}, type={key[2]}"
            )
            assert q.na1_unused == expected[2], (
                f"Mismatch B=2: rate={key[0]}, freq={key[1]}, type={key[2]}"
            )
