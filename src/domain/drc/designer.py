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
    gain_compute: int  # REG23
    noise_gate: int  # REG24
    timeout_gain_balance: int  # REG25
    makeup_gain: int  # REG26
    max_output: int  # REG27


class DRCDesigner(Protocol):
    """Port: given DRC parameters, produce register values."""

    def design(self, params: DRCParams) -> DrcRegisters: ...
