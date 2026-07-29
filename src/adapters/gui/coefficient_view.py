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

from PySide6.QtWidgets import (
    QGroupBox,
    QHeaderView,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)


class CoefficientView(QGroupBox):
    """Table showing quantized hex coefficients for all 7 bands."""

    FREQ_LABELS = ["1k", "4k", "7k", "10k", "13k", "16k", "19k"]

    def __init__(self, parent=None):
        super().__init__("Coefficients", parent)
        self._table = QTableWidget(3, 7)
        self._table.setHorizontalHeaderLabels(self.FREQ_LABELS)
        self._table.setVerticalHeaderLabels(["B=0 (b0/b2)", "B=1 (b1/a2)", "B=2 (a1/-)"])
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self._table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout = QVBoxLayout(self)
        layout.addWidget(self._table)

    def update_coeffs(self, packed: list[tuple[int, int, int]]) -> None:
        """Update table with packed coefficients per band.

        Args:
            packed: list of (b0_b2, b1_na2, na1_unused) per band, length 7.
        """
        for col in range(7):
            if col < len(packed):
                b0b2, b1na2, na1 = packed[col]
                self._table.setItem(0, col, QTableWidgetItem(f"0x{b0b2:08X}"))
                self._table.setItem(1, col, QTableWidgetItem(f"0x{b1na2:08X}"))
                self._table.setItem(2, col, QTableWidgetItem(f"0x{na1:08X}"))
            else:
                for row in range(3):
                    self._table.setItem(row, col, QTableWidgetItem("—"))
