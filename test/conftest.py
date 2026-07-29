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

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent
COE_ARRAY_PATH = ROOT / "doc" / "old_backup" / "coe_array.txt"


def pytest_addoption(parser):
    parser.addoption(
        "--real-hardware", action="store_true", default=False,
        help="Run tests against real SdwRegisterTool.exe"
    )


@pytest.fixture(scope="session")
def coe_array_path():
    return COE_ARRAY_PATH


@pytest.fixture(scope="session")
def use_real_hardware(request):
    return request.config.getoption("--real-hardware")


@pytest.fixture(scope="session")
def coe_entries():
    """Parse coe_array.txt into list of test entries.

    Returns list of dicts with keys: rate, freq, ftype, bgroup, packed32
    """
    entries = []
    pattern = re.compile(
        r'fs(\d+)k_f(\d+)k_coe\s+\[\s*(\d+)\]\s*\[\s*(\d+)\]\s*=\s*32\'h([0-9A-Fa-f]+)'
    )
    text = COE_ARRAY_PATH.read_text()
    for match in pattern.finditer(text):
        entries.append({
            "rate": int(match.group(1)) * 1000,
            "freq": int(match.group(2)) * 1000,
            "ftype": int(match.group(3)),
            "bgroup": int(match.group(4)),
            "packed32": int(match.group(5), 16),
        })
    return entries
