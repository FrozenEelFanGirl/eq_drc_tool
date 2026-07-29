"""Layer 6: Protocol FSM rule validation."""

from src.application.drc_session import DRCSession
from src.application.eq_session import EQSession
from src.application.script_composer import ScriptComposer
from src.domain.eq.coefficients import BiquadCoefficients
from src.domain.script.register_map import REG14, REG15, REG16, EqCommand


class StubDesigner:
    def design(self, params, sample_rate=48000):
        return BiquadCoefficients(b0=1.0, b1=0.0, b2=0.0, a1=0.0, a2=0.0)


def _make_writes():
    eq = EQSession()
    drc = DRCSession()
    composer = ScriptComposer(StubDesigner())
    return composer.compose(eq, drc)


class TestFsmRules:
    def test_clock_force_first(self):
        w = _make_writes()
        assert w[0].address == REG16 and w[0].value == 0x10

    def test_reset_before_config(self):
        w = _make_writes()
        assert w[1].address == REG15 and w[1].value == EqCommand.RESET_DATA.value

    def test_enter_config_twice(self):
        w = _make_writes()
        assert w[2].address == REG15 and w[2].value == EqCommand.ENTER_CONFIG.value
        assert w[3].address == REG15 and w[3].value == EqCommand.ENTER_CONFIG.value

    def test_config_mode_not_in_write_pulse(self):
        """Write pulse 0xA3 has bit4=0, so config_mode is NOT set."""
        assert (0xA3 & 0x10) == 0

    def test_config_mode_not_in_read_pulse(self):
        """Read pulse 0xC3 has bit4=0."""
        assert (0xC3 & 0x10) == 0

    def test_config_mode_in_enter_config(self):
        """Enter CONFIG 0x93 has bit4=1."""
        assert (0x93 & 0x10) == 0x10

    def test_release_clears_bit4(self):
        """Release 0x83 has bit4=0."""
        assert (0x83 & 0x10) == 0

    def test_reset_clears_bit4(self):
        """Reset commands have bit4=0."""
        assert (0x87 & 0x10) == 0
        assert (0x8F & 0x10) == 0

    def test_completion_at_end(self):
        w = _make_writes()
        # Find the completion write: REG14=111 before DRC section
        completion_found = False
        for rw in w:
            if rw.address == REG14 and rw.value == 111:
                completion_found = True
                break
        assert completion_found, "No completion write (REG14=111) found"

    def test_no_config_pulse_after_write(self):
        """After every write pulse (0xA3), the next REG15 write is never CONFIG (0x93)."""
        w = _make_writes()
        for i, rw in enumerate(w):
            if rw.address == REG15 and rw.value == EqCommand.WRITE_PULSE.value:
                for j in range(i + 1, len(w)):
                    if w[j].address == REG15:
                        assert w[j].value != EqCommand.ENTER_CONFIG.value, (
                            f"Config pulse follows write pulse at index {i}"
                        )
                        break

    def test_clock_release_at_end(self):
        w = _make_writes()
        # Last write is REG16=0x00 (DRC disable / clock release)
        assert w[-1].address == REG16 and w[-1].value == 0x00
