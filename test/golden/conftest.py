import re
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent.parent
COE_ARRAY = ROOT / "doc" / "old_backup" / "coe_array.txt"


def load_coe_array() -> list[dict]:
    """Parse coe_array.txt into list of test entries.

    Returns list of dicts with keys: rate, freq, ftype, bgroup, packed32
    """
    entries = []
    pattern = re.compile(
        r'fs(\d+)k_f(\d+)k_coe\s+\[\s*(\d+)\]\s*\[\s*(\d+)\]\s*=\s*32\'h([0-9A-Fa-f]+)'
    )
    text = COE_ARRAY.read_text()
    for match in pattern.finditer(text):
        entries.append({
            "rate": int(match.group(1)) * 1000,
            "freq": int(match.group(2)) * 1000,
            "ftype": int(match.group(3)),
            "bgroup": int(match.group(4)),
            "packed32": int(match.group(5), 16),
        })
    return entries


@pytest.fixture(scope="session")
def coe_entries():
    return load_coe_array()


def coe_by_key(entries: list[dict], rate: int, freq: int, ftype: int) -> dict[int, int]:
    """Extract {bgroup: packed32} for a given (rate, freq, ftype)."""
    return {
        e["bgroup"]: e["packed32"]
        for e in entries
        if e["rate"] == rate and e["freq"] == freq and e["ftype"] == ftype
    }
