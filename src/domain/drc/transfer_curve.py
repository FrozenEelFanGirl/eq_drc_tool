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

from .params import DRCParams


def evaluate(params: DRCParams, x_min: float = -80, x_max: float = 36,
             num_points: int = 512) -> tuple[np.ndarray, np.ndarray]:
    """Compute DRC static transfer curve.

    Hardware behavior:
      - Input below noise_gate → forced to zero (output = -inf dB)
      - Input below threshold → linear: output = input + makeup_gain
      - Input between threshold and max_output → compressed
      - Input above max_output → clamped to max_output

    Returns (input_dB, output_dB).
    """
    in_db = np.linspace(x_min, x_max, num_points)

    thr = params.threshold_db
    ratio = params.ratio
    makeup = params.makeup_gain_db
    gate = params.noise_gate_db
    cap = params.max_output_db

    # Below gate: forced to zero → plot floor at x_min
    out_db = np.full_like(in_db, x_min)

    # Linear region: gate < in <= threshold
    lin = (in_db > gate) & (in_db <= thr)
    out_db[lin] = in_db[lin] + makeup

    # Compressed region: threshold < in
    if np.isfinite(ratio):
        comp = in_db > thr
        out_db[comp] = thr + (in_db[comp] - thr) * ratio + makeup
    else:
        comp = in_db > thr
        out_db[comp] = thr + makeup

    # Max output clamp: clamps the OUTPUT after compression
    over = out_db > cap
    out_db[over] = cap

    return in_db, out_db
