from enum import IntEnum

# --- Register addresses ---
REG10 = 0x2060  # EQ coefficient 1 MSB
REG11 = 0x2061  # EQ coefficient 1 LSB
REG12 = 0x2062  # EQ coefficient 2 MSB
REG13 = 0x2063  # EQ coefficient 2 LSB
REG14 = 0x2064  # EQ bank/address command
REG15 = 0x2065  # EQ control command

REG16 = 0x2066  # DRC control command
REG17 = 0x2067  # DRC threshold MSB
REG18 = 0x2068  # DRC threshold LSB
REG19 = 0x2069  # DRC update window length
REG20 = 0x206A  # DRC attack coeff MSB
REG21 = 0x206B  # DRC release coeff MSB
REG22 = 0x206C  # DRC ratio + attack/release LSBs
REG23 = 0x206D  # DRC gain compute floating
REG24 = 0x206E  # DRC noise gate
REG25 = 0x206F  # DRC timeout + gain balance
REG26 = 0x205E  # DRC makeup gain
REG27 = 0x205F  # DRC max output

# --- EQ address map ---
# Each bank has 7 stages × 3 groups = 21 addresses.
# Addresses are 7-bit (0–127), loaded into REG14 bits 6:0.
BANK_BASE = {48000: 48, 96000: 69, 192000: 90}
COMPLETION_ADDR = 111  # Write to this address triggers CONFIG → WAIT
BANDS_COUNT = 7
GROUPS_PER_BAND = 3  # B=0, B=1, B=2


def eq_addr(sample_rate: int, stage: int, group: int) -> int:
    """REG14 address for a given sample rate, stage (0-6), and B-group (0-2)."""
    base = BANK_BASE[sample_rate]
    return base + stage * GROUPS_PER_BAND + group


# --- REG15 EQ commands ---
class EqCommand(IntEnum):
    ENTER_CONFIG = 0x93  # config_mode + manual_en + manual_mode
    WRITE_PULSE = 0xA3   # write_en + manual_en + manual_mode (bit4=0)
    READ_PULSE = 0xC3    # read_en + manual_en + manual_mode (bit4=0)
    RELEASE = 0x83       # manual_en + manual_mode (universal clear after pulse)
    RESET_DATA = 0x87    # manual_reset + manual_en + manual_mode (data path only)
    RESET_DATA_COE = 0x8F  # reset_mode + manual_reset + manual_en + manual_mode


# --- REG16 DRC commands ---
class DrcCommand(IntEnum):
    DISABLE = 0x00           # DRC fully off
    CLOCK_FORCE_NO_DRC = 0x50  # bit6+5+4 (disable UMP check, disable UMP timeout, force clock)
    ENABLE = 0xC3            # disable AE + disable UMP check + manual_en + manual_mode


# --- DRC parameter registers (for script composer ordering) ---
DRC_PARAM_REGISTERS = [
    REG17, REG18, REG19, REG20, REG21, REG22,
    REG23, REG24, REG25, REG26, REG27,
]
