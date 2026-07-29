"""Layer 3: Register address generation."""

import pytest

from src.domain.script.register_map import (
    COMPLETION_ADDR,
    BANK_BASE,
    eq_addr,
)


class TestAddressGeneration:
    def test_bank_bases(self):
        assert BANK_BASE[48000] == 48
        assert BANK_BASE[96000] == 69
        assert BANK_BASE[192000] == 90

    def test_bank0_stage0_b0(self):
        assert eq_addr(48000, 0, 0) == 0x30

    def test_bank0_stage0_b1(self):
        assert eq_addr(48000, 0, 1) == 0x31

    def test_bank0_stage0_b2(self):
        assert eq_addr(48000, 0, 2) == 0x32

    def test_bank0_stage6_b2(self):
        assert eq_addr(48000, 6, 2) == 0x44

    def test_bank1_stage0_b0(self):
        assert eq_addr(96000, 0, 0) == 0x45

    def test_bank2_stage6_b2(self):
        assert eq_addr(192000, 6, 2) == 0x6E

    def test_completion_addr(self):
        assert COMPLETION_ADDR == 0x6F

    def test_bank0_all_addresses(self):
        """All 21 addresses in bank 0 are 0x30–0x44."""
        addrs = set()
        for stage in range(7):
            for group in range(3):
                a = eq_addr(48000, stage, group)
                assert 0x30 <= a <= 0x44
                addrs.add(a)
        assert len(addrs) == 21

    def test_no_overlap_between_banks(self):
        b0 = {eq_addr(48000, s, g) for s in range(7) for g in range(3)}
        b1 = {eq_addr(96000, s, g) for s in range(7) for g in range(3)}
        b2 = {eq_addr(192000, s, g) for s in range(7) for g in range(3)}
        assert b0.isdisjoint(b1)
        assert b1.isdisjoint(b2)
        assert b0.isdisjoint(b2)

    def test_bad_sample_rate(self):
        with pytest.raises(KeyError):
            eq_addr(44100, 0, 0)
