from dataclasses import dataclass


@dataclass(frozen=True)
class DRCParams:
    """DRC hardware register parameters (mutable for GUI binding)."""

    threshold_db: float = -24.0       # REG17/18: 1.7.8 signed, [-80, 0] dB
    ratio_idx: int = 4                # REG22[7:5]: 0=∞, 1=0.125, ..., 7=0.875
    attack_val: int = 0               # REG20+22[3:2]: 10-bit [0, 1023]
    release_val: int = 0              # REG21+22[1:0]: 10-bit [0, 1023]
    update_window: int = 96           # REG19: [0, 255], ≥96 recommended
    gain_compute: int = 0x42          # REG23: [0x40, 0xFF]
    noise_gate_db: float = -69.977    # REG24: val [0,255], dB [-88.98, -57.10]
    gain_balance: int = 0             # REG25[1:0]: 0=indep, 1=L, 2=R, 3=max
    makeup_gain_db: float = 0.0       # REG26: absolute dB [0, 31.875]
    max_output_db: float = 0.02       # REG27: dB [-88.98, +166.02]
    extended_window: bool = False     # allow update_window < 96

    @property
    def ratio(self) -> float:
        """Compression slope (hardware ratio)."""
        return [float('inf'), 0.125, 0.25, 0.375, 0.5, 0.625, 0.75, 0.875][self.ratio_idx]
