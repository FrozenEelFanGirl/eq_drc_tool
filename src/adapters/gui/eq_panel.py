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
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from ...domain.eq.params import FilterParams, FilterType
from ..gui.i18n import Lang, get_language, tr
from ..gui.widgets import HelpButton

STAGES = 7
FREQ_MIN = 20.0
FREQ_MAX = 20000.0
DEFAULT_FREQS = [1000, 4000, 7000, 10000, 13000, 16000, 19000]


def _freq_to_slider(freq: float) -> int:
    return int(1000 * np.log10(freq / FREQ_MIN) / np.log10(FREQ_MAX / FREQ_MIN))


def _slider_to_freq(val: int) -> float:
    return round(FREQ_MIN * 10.0 ** (val / 1000 * np.log10(FREQ_MAX / FREQ_MIN)))


def _q_to_slider(q: float) -> int:
    if q <= 1.0:
        return int((q - 0.1) / 0.9 * 40)
    return int(40 + (q - 1.0) / 9.0 * 60)


def _slider_to_q(val: int) -> float:
    if val <= 40:
        return round(0.1 + val / 40 * 0.9, 2)
    return round(1.0 + (val - 40) / 60 * 9.0, 2)


class _BandStrip(QGroupBox):

    def __init__(self, index: int, parent=None):
        super().__init__(parent)
        self._index = index
        self._freq = DEFAULT_FREQS[index]

        self._type_combo = QComboBox()

        self._freq_slider = QSlider(Qt.Horizontal)
        self._freq_slider.setRange(0, 1000)
        self._freq_slider.setValue(_freq_to_slider(self._freq))
        self._freq_spin = QDoubleSpinBox()
        self._freq_spin.setRange(FREQ_MIN, FREQ_MAX)
        self._freq_spin.setValue(self._freq)
        self._freq_spin.setDecimals(0)
        self._freq_spin.setSuffix(" Hz")

        self._gain_slider = QSlider(Qt.Horizontal)
        self._gain_slider.setRange(-200, 200)
        self._gain_spin = QDoubleSpinBox()
        self._gain_spin.setRange(-20, 20)
        self._gain_spin.setSuffix(" dB")

        self._q_slider = QSlider(Qt.Horizontal)
        self._q_slider.setRange(0, 100)
        self._q_slider.setValue(_q_to_slider(1.0))
        self._q_spin = QDoubleSpinBox()
        self._q_spin.setRange(0.1, 10)
        self._q_spin.setValue(1.0)
        self._q_spin.setDecimals(2)
        self._q_spin.setSingleStep(0.1)

        self._bypass_cb = QCheckBox()
        self._bypass_cb.setChecked(True)

        self._warn_label = QLabel("")
        self._warn_label.setStyleSheet("color: red; font-weight: bold;")
        self._warn_label.setVisible(False)

        # Wire slider ↔ spinbox
        self._freq_slider.valueChanged.connect(
            lambda v: self._freq_spin.setValue(_slider_to_freq(v)))
        self._freq_spin.valueChanged.connect(
            lambda v: self._freq_slider.setValue(_freq_to_slider(v)))
        self._gain_slider.valueChanged.connect(
            lambda v: self._gain_spin.setValue(v / 10.0))
        self._gain_spin.valueChanged.connect(
            lambda v: self._gain_slider.setValue(int(v * 10)))
        self._q_slider.valueChanged.connect(
            lambda v: self._q_spin.setValue(_slider_to_q(v)))
        self._q_spin.valueChanged.connect(
            lambda v: self._q_slider.setValue(_q_to_slider(v)))

        from ..gui.i18n import get_language, tr as _tr

        lang = get_language()

        def _lbl(key: str) -> QWidget:
            w = QWidget()
            l = QHBoxLayout(w)
            l.setContentsMargins(0, 0, 0, 0)
            text = QLabel(_tr(key, lang))
            help_icon = HelpButton(key)
            l.addWidget(text)
            l.addWidget(help_icon)
            l.addStretch()
            w._text_label = text
            w._help_icon = help_icon
            return w

        self._lbl_bypass_w = _lbl("eq.bypass")
        self._lbl_type_w = _lbl("eq.type")
        self._lbl_freq_w = _lbl("eq.freq")
        self._lbl_gain_w = _lbl("eq.gain")
        self._lbl_q_w = _lbl("eq.q")

        self._bypass_cb.setText(_tr("eq.bypass", lang))
        self.setTitle(_tr("eq.stage", lang).format(self._index + 1))
        self._type_combo.addItems([_tr(f"ftype.{i}", lang) for i in range(7)])

        self._freq_ctrl = self._make_hbox(self._freq_slider, self._freq_spin)
        self._gain_ctrl = self._make_hbox(self._gain_slider, self._gain_spin)
        self._q_ctrl = self._make_hbox(self._q_slider, self._q_spin)

        self._form = QFormLayout(self)
        self._form.addRow(self._lbl_bypass_w, self._make_hbox(self._bypass_cb, self._warn_label))
        self._form.addRow(self._lbl_type_w, self._type_combo)
        self._form.addRow(self._lbl_freq_w, self._freq_ctrl)
        self._form.addRow(self._lbl_gain_w, self._gain_ctrl)
        self._form.addRow(self._lbl_q_w, self._q_ctrl)

        self._type_combo.currentIndexChanged.connect(self._update_param_state)
        self._update_param_state()

    def _make_hbox(self, a: QWidget, b: QWidget) -> QWidget:
        w = QWidget()
        layout = QHBoxLayout(w)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(a, 1)
        layout.addWidget(b, 0)
        return w

    def _update_param_state(self) -> None:
        """Enable/disable controls based on current filter type."""
        ftype = FilterType(self._type_combo.currentIndex())

        freq_ok = ftype != FilterType.BYPASS
        gain_ok = ftype not in (FilterType.BYPASS, FilterType.NOTCH,
                                 FilterType.HPF, FilterType.LPF)
        q_ok = ftype != FilterType.BYPASS

        for lbl, ctrl, ok in [
            (self._lbl_freq_w, self._freq_ctrl, freq_ok),
            (self._lbl_gain_w, self._gain_ctrl, gain_ok),
            (self._lbl_q_w, self._q_ctrl, q_ok),
        ]:
            lbl.setEnabled(ok)
            ctrl.setEnabled(ok)

    @property
    def filter_params(self) -> FilterParams:
        return FilterParams(
            freq=float(self._freq_spin.value()),
            filter_type=FilterType(self._type_combo.currentIndex()),
            gain_db=self._gain_spin.value(),
            Q=self._q_spin.value(),
        )

    @property
    def bypassed(self) -> bool:
        return self._bypass_cb.isChecked()

    def set_warning(self, msg: str | None) -> None:
        if msg:
            self._warn_label.setText(msg)
            self._warn_label.setVisible(True)
        else:
            self._warn_label.setVisible(False)

    def set_params(self, params: FilterParams) -> None:
        """Set controls from a FilterParams value (for config import)."""
        self._freq_spin.setValue(params.freq)
        self._type_combo.setCurrentIndex(params.filter_type.value)
        self._gain_spin.setValue(params.gain_db)
        self._q_spin.setValue(params.Q)
        self._bypass_cb.setChecked(False)

    def set_bypassed(self) -> None:
        self._bypass_cb.setChecked(True)

    def on_changed(self, slot) -> None:
        self._type_combo.currentIndexChanged.connect(lambda _: slot())
        self._freq_spin.valueChanged.connect(lambda _: slot())
        self._gain_spin.valueChanged.connect(lambda _: slot())
        self._q_spin.valueChanged.connect(lambda _: slot())
        self._bypass_cb.toggled.connect(lambda _: slot())

    def refresh_labels(self, lang: Lang) -> None:
        self.setTitle(tr("eq.stage", lang).format(self._index + 1))
        self._bypass_cb.setText(tr("eq.bypass", lang))

        self._type_combo.blockSignals(True)
        current = self._type_combo.currentIndex()
        self._type_combo.clear()
        self._type_combo.addItems([tr(f"ftype.{i}", lang) for i in range(7)])
        self._type_combo.setCurrentIndex(current)
        self._type_combo.blockSignals(False)

        # Update label text + tooltip
        for w, key in [
            (self._lbl_bypass_w, "eq.bypass"),
            (self._lbl_type_w, "eq.type"),
            (self._lbl_freq_w, "eq.freq"),
            (self._lbl_gain_w, "eq.gain"),
            (self._lbl_q_w, "eq.q"),
        ]:
            w._text_label.setText(tr(key, lang))
            w._help_icon.refresh_language(key)


class EQPanel(QScrollArea):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWidgetResizable(True)
        container = QWidget()
        layout = QVBoxLayout(container)
        self._strips: list[_BandStrip] = []
        for i in range(STAGES):
            strip = _BandStrip(i)
            self._strips.append(strip)
            layout.addWidget(strip)
        layout.addStretch()
        self.setWidget(container)

    @property
    def strips(self) -> list[_BandStrip]:
        return self._strips

    def refresh_language(self, lang: Lang) -> None:
        for s in self._strips:
            s.refresh_labels(lang)
