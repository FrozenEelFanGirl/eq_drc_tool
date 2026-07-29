# Copyright (c) 2026 FrozenEelFanGirl & Senary
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import numpy as np

from .coefficients import BiquadCoefficients


def _biquad_response(coeffs: BiquadCoefficients, freqs: np.ndarray,
                     sample_rate: int) -> np.ndarray:
    """Compute H(z) for a single biquad at given frequencies."""
    b0, b1, b2, a1, a2 = coeffs.b0, coeffs.b1, coeffs.b2, coeffs.a1, coeffs.a2
    omega = 2.0 * np.pi * freqs / sample_rate
    z_inv = np.exp(-1j * omega)
    z_inv2 = z_inv * z_inv
    num = b0 + b1 * z_inv + b2 * z_inv2
    den = 1.0 + a1 * z_inv + a2 * z_inv2
    return num / den


def evaluate(coefficients: list[BiquadCoefficients], sample_rate: int,
             num_points: int = 512) -> tuple[np.ndarray, np.ndarray]:
    """Compute cascaded magnitude response (dB) at log-spaced frequencies.

    Returns (frequencies, magnitude_db).
    """
    freqs = np.logspace(np.log10(20), np.log10(20000), num_points)
    H_total = np.ones(num_points, dtype=complex)
    for c in coefficients:
        if c is not None:
            H_total *= _biquad_response(c, freqs, sample_rate)
    mag_db = 20.0 * np.log10(np.abs(H_total) + 1e-12)
    return freqs, mag_db


def evaluate_per_band(coefficients: list[BiquadCoefficients], sample_rate: int,
                      num_points: int = 512) -> tuple[np.ndarray, list[np.ndarray]]:
    """Compute magnitude response for each individual band.

    Returns (frequencies, [mag_db_per_band, ...]).
    """
    freqs = np.logspace(np.log10(20), np.log10(20000), num_points)
    band_mags = []
    for c in coefficients:
        if c is not None:
            H = _biquad_response(c, freqs, sample_rate)
            band_mags.append(20.0 * np.log10(np.abs(H) + 1e-12))
        else:
            band_mags.append(np.zeros(num_points))
    return freqs, band_mags


def evaluate_phase(coefficients: list[BiquadCoefficients], sample_rate: int,
                   num_points: int = 512) -> tuple[np.ndarray, np.ndarray]:
    """Compute cascaded phase response (degrees) at log-spaced frequencies.

    Returns (frequencies, phase_deg).
    """
    freqs = np.logspace(np.log10(20), np.log10(20000), num_points)
    H_total = np.ones(num_points, dtype=complex)
    for c in coefficients:
        if c is not None:
            H_total *= _biquad_response(c, freqs, sample_rate)
    phase_deg = np.angle(H_total, deg=True)
    return freqs, phase_deg


def evaluate_phase_per_band(coefficients: list[BiquadCoefficients], sample_rate: int,
                             num_points: int = 512) -> tuple[np.ndarray, list[np.ndarray]]:
    """Compute phase response for each individual band.

    Returns (frequencies, [phase_deg_per_band, ...]).
    """
    freqs = np.logspace(np.log10(20), np.log10(20000), num_points)
    band_phases = []
    for c in coefficients:
        if c is not None:
            H = _biquad_response(c, freqs, sample_rate)
            band_phases.append(np.angle(H, deg=True))
        else:
            band_phases.append(np.zeros(num_points))
    return freqs, band_phases


def evaluate_quantized_phase(float_coeffs: list[BiquadCoefficients],
                              sample_rate: int,
                              num_points: int = 512) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Compute float vs. Q2.14 quantized phase responses for comparison.

    Returns (frequencies, float_phase_deg, quantized_phase_deg).
    """
    from .quantizer import quantize, unpack_to_coeffs

    freqs = np.logspace(np.log10(20), np.log10(20000), num_points)
    H_float = np.ones(num_points, dtype=complex)
    H_quant = np.ones(num_points, dtype=complex)

    for c in float_coeffs:
        if c is not None:
            H_float *= _biquad_response(c, freqs, sample_rate)
            cq = unpack_to_coeffs(quantize(c))
            H_quant *= _biquad_response(cq, freqs, sample_rate)

    phase_float = np.angle(H_float, deg=True)
    phase_quant = np.angle(H_quant, deg=True)
    return freqs, phase_float, phase_quant


def evaluate_quantized_response(float_coeffs: list[BiquadCoefficients],
                                 sample_rate: int,
                                 num_points: int = 512) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Compute float vs. Q2.14 quantized magnitude responses for comparison.

    Returns (frequencies, float_mag_db, quantized_mag_db).
    """
    from .quantizer import quantize, unpack_to_coeffs

    freqs = np.logspace(np.log10(20), np.log10(20000), num_points)
    H_float = np.ones(num_points, dtype=complex)
    H_quant = np.ones(num_points, dtype=complex)

    for c in float_coeffs:
        if c is not None:
            H_float *= _biquad_response(c, freqs, sample_rate)
            cq = unpack_to_coeffs(quantize(c))
            H_quant *= _biquad_response(cq, freqs, sample_rate)

    mag_float = 20.0 * np.log10(np.abs(H_float) + 1e-12)
    mag_quant = 20.0 * np.log10(np.abs(H_quant) + 1e-12)
    return freqs, mag_float, mag_quant
