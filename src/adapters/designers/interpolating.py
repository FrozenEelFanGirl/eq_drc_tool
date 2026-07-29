import re
from pathlib import Path

from ...domain.eq.coefficients import BiquadCoefficients
from ...domain.eq.designer import DesignedCoefficients
from ...domain.eq.params import FilterParams, FilterType
from ...domain.eq.quantizer import QuantizedCoefficients, unpack_to_coeffs

# coe_array.txt lookup key → {B0: packed32, B1: packed32, B2: packed32}
_LUT: dict[tuple[int, int, FilterType], tuple[int, int, int]] = {}


def _parse_coe_array(path: Path) -> dict[tuple[int, int, FilterType], tuple[int, int, int]]:
    """Parse coe_array.txt into lookup table.

    Returns {(sample_rate, freq, filter_type): (b0b2, b1na2, na1_unused)}
    """
    lut: dict[tuple[int, int, FilterType], tuple[int, int, int]] = {}
    pattern = re.compile(
        r'fs(\d+)k_f(\d+)k_coe\s+\[\s*(\d+)\]\s*\[\s*(\d+)\]\s*=\s*32\'h([0-9A-Fa-f]+)'
    )

    text = path.read_text()
    for match in pattern.finditer(text):
        rate = int(match.group(1)) * 1000
        freq = int(match.group(2)) * 1000
        ftype = FilterType(int(match.group(3)))
        bgroup = int(match.group(4))
        value = int(match.group(5), 16)

        key = (rate, freq, ftype)
        if key not in lut:
            lut[key] = [0, 0, 0]
        lut[key][bgroup] = value

    return {k: tuple(v) for k, v in lut.items()}  # type: ignore[arg-type]


def load_coefficients(path: str | Path | None = None) -> None:
    """Load coefficient lookup table from coe_array.txt."""
    global _LUT
    if path is None:
        path = Path(__file__).parent.parent.parent.parent / 'doc' / 'old_backup' / 'coe_array.txt'
    _LUT = _parse_coe_array(Path(path))


class InterpolatingDesigner:
    """Phase 1: exact lookup from pre-computed coefficients.

    Only supports exact matches at the 105 sampled points.
    Interpolation between points is a future enhancement.
    """

    def design(self, params: FilterParams, sample_rate: int) -> DesignedCoefficients:
        if not _LUT:
            raise RuntimeError(
                "Coefficient LUT not loaded. Call load_coefficients() first."
            )

        key = (sample_rate, int(params.freq), params.filter_type)
        if key in _LUT:
            b0_b2, b1_na2, na1 = _LUT[key]
            q = QuantizedCoefficients(b0_b2=b0_b2, b1_na2=b1_na2, na1_unused=na1)
            return DesignedCoefficients(float_coeffs=unpack_to_coeffs(q), quantized=q)

        raise KeyError(
            f"No coefficient data for rate={sample_rate}, freq={params.freq}, "
            f"type={params.filter_type.name}"
        )
