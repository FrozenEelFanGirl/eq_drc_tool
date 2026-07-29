from ...domain.script.commands import RegisterWrite


def _addr_name(address: int) -> str:
    """Return human-readable register name for an address, or hex."""
    names = {
        0x2060: "REG10", 0x2061: "REG11", 0x2062: "REG12", 0x2063: "REG13",
        0x2064: "REG14", 0x2065: "REG15", 0x2066: "REG16", 0x2067: "REG17",
        0x2068: "REG18", 0x2069: "REG19", 0x206A: "REG20", 0x206B: "REG21",
        0x206C: "REG22", 0x206D: "REG23", 0x206E: "REG24", 0x206F: "REG25",
        0x205E: "REG26", 0x205F: "REG27",
    }
    return names.get(address, f"0x{address:08X}")


class BatScriptFormatter:
    """Format RegisterWrite list → .bat file text."""

    def format(self, writes: list[RegisterWrite]) -> str:
        lines = ["@echo off", ""]
        for rw in writes:
            name = _addr_name(rw.address)
            addr_hex = f"0x{rw.address:08X}"
            val_hex = f"0x{rw.value:02X}"
            lines.append(f'echo "Write CT_DAC_{name} {val_hex}"')
            lines.append(
                f'powershell -Command ".\\SdwRegisterTool.ps1'
                f' -WriteAddress {addr_hex} -Value {val_hex}"'
            )
            lines.append("")
        lines.append("pause")
        return "\r\n".join(lines) + "\r\n"
