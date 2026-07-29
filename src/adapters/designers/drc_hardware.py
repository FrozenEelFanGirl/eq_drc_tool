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
