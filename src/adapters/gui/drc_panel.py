import numpy as np
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox, QComboBox, QDoubleSpinBox, QFormLayout, QGroupBox,
    QHBoxLayout, QLabel, QScrollArea, QSlider, QSpinBox,
    QVBoxLayout, QWidget,
)

from ...domain.drc.params import DRCParams
from ..gui.i18n import Lang, get_language, tr
from ..gui.widgets import HelpButton

RATIO_LABELS = [f"∞:{1}", f"{8}:{1}", f"{4}:{1}", f"{2.67}:{1}",
                f"{2}:{1}", f"{1.6}:{1}", f"{1.33}:{1}", f"{1.14}:{1}"]
BALANCE_MODES = ["Independent L/R", "Use Left", "Use Right", "Use Max"]
FS_VALUES = [48000, 96000, 192000]


def _attack_release_time(reg10: int, fs: int) -> float:
    """Compute attack/release time in ms from 10-bit register value."""
    q1_15 = 0x7C00 | reg10
    coeff = q1_15 / 32768.0
    if coeff >= 1.0 or coeff <= 0.0:
        return float('inf')
    s = -np.log(9) / (fs * np.log(coeff))
    return s * 1000.0



def _pair(slider: QSlider, spin: QWidget) -> QWidget:
    w = QWidget()
    l = QHBoxLayout(w)
    l.setContentsMargins(0, 0, 0, 0)
    l.addWidget(slider, 1)
    l.addWidget(spin)
    return w


class DRCPanel(QScrollArea):
    """DRC hardware register controls."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWidgetResizable(True)

        self._enable_cb = QCheckBox()

        # Threshold: [-80, 0] dB, step 1/256 → slider [0, 20480]
        self._thr_slider = QSlider(Qt.Horizontal)
        self._thr_slider.setRange(0, 20480)
        self._thr_slider.setValue(56 * 256)  # -24 dB
        self._thr_spin = QDoubleSpinBox()
        self._thr_spin.setRange(-80, 0)
        self._thr_spin.setDecimals(3)
        self._thr_spin.setSingleStep(1.0 / 256)
        self._thr_spin.setValue(-24)
        self._thr_spin.setSuffix(" dB")
        self._thr_slider.valueChanged.connect(
            lambda v: self._thr_spin.setValue(-80 + v / 256))
        self._thr_spin.valueChanged.connect(
            lambda v: self._thr_slider.setValue(round((v + 80) * 256)))

        # Update Window: [96, 255] default, [0, 255] if extended
        self._win_slider = QSlider(Qt.Horizontal)
        self._win_slider.setRange(96, 255)
        self._win_slider.setValue(96)
        self._win_spin = QSpinBox()
        self._win_spin.setRange(96, 255)
        self._win_spin.setValue(96)
        self._win_slider.valueChanged.connect(self._win_spin.setValue)
        self._win_spin.valueChanged.connect(self._win_slider.setValue)
        self._win_extend = QCheckBox()
        self._win_extend.setChecked(False)
        self._win_extend.toggled.connect(self._on_win_extend)

        # Attack: 10-bit [0, 1023]
        self._att_slider = QSlider(Qt.Horizontal)
        self._att_slider.setRange(0, 1023)
        self._att_slider.setValue(0)
        self._att_spin = QSpinBox()
        self._att_spin.setRange(0, 1023)
        self._att_slider.valueChanged.connect(self._att_spin.setValue)
        self._att_spin.valueChanged.connect(self._att_slider.setValue)
        self._att_time_label = QLabel()

        # Release: 10-bit [0, 1023]
        self._rel_slider = QSlider(Qt.Horizontal)
        self._rel_slider.setRange(0, 1023)
        self._rel_slider.setValue(0)
        self._rel_spin = QSpinBox()
        self._rel_spin.setRange(0, 1023)
        self._rel_slider.valueChanged.connect(self._rel_spin.setValue)
        self._rel_spin.valueChanged.connect(self._rel_slider.setValue)
        self._rel_time_label = QLabel()

        # Ratio: 8-value combo
        self._ratio_combo = QComboBox()
        self._ratio_combo.addItems(RATIO_LABELS)
        self._ratio_combo.setCurrentIndex(4)

        # Gain Compute: [0x40, 0xFF] = [64, 255]
        self._gc_slider = QSlider(Qt.Horizontal)
        self._gc_slider.setRange(64, 255)
        self._gc_slider.setValue(0x42)
        self._gc_spin = QSpinBox()
        self._gc_spin.setRange(64, 255)
        self._gc_spin.setValue(0x42)
        self._gc_spin.setDisplayIntegerBase(16)
        self._gc_slider.valueChanged.connect(self._gc_spin.setValue)
        self._gc_spin.valueChanged.connect(self._gc_slider.setValue)

        # Noise Gate: val [0, 255], dB [-88.98, -57.10]
        self._ng_slider = QSlider(Qt.Horizontal)
        self._ng_slider.setRange(0, 255)
        self._ng_slider.setValue(152)   # -69.977 dB
        self._ng_spin = QDoubleSpinBox()
        self._ng_spin.setRange(-88.98, -57.10)
        self._ng_spin.setDecimals(3)
        self._ng_spin.setSingleStep(0.125)
        self._ng_spin.setValue(-69.977)
        self._ng_spin.setSuffix(" dB")
        self._ng_slider.valueChanged.connect(
            lambda v: self._ng_spin.setValue(
                (v * 32 - 0x58FA) / 256.0))
        self._ng_spin.valueChanged.connect(
            lambda v: self._ng_slider.setValue(
                max(0, min(255, round((v * 256 + 0x58FA) / 32)))))

        # Gain Balance: 4-mode combo
        self._bal_combo = QComboBox()
        self._bal_combo.addItems(BALANCE_MODES)

        # Makeup Gain: val [0, 255], dB [0, 31.875]
        self._mu_slider = QSlider(Qt.Horizontal)
        self._mu_slider.setRange(0, 255)
        self._mu_spin = QDoubleSpinBox()
        self._mu_spin.setRange(0, 31.875)
        self._mu_spin.setDecimals(3)
        self._mu_spin.setSingleStep(0.125)
        self._mu_spin.setSuffix(" dB")
        self._mu_slider.valueChanged.connect(
            lambda v: self._mu_spin.setValue(v / 8.0))
        self._mu_spin.valueChanged.connect(
            lambda v: self._mu_slider.setValue(round(v * 8)))

        # Max Output: val [0, 255], dB [-88.98, +166.02]
        self._mo_slider = QSlider(Qt.Horizontal)
        self._mo_slider.setRange(0, 255)
        self._mo_slider.setValue(89)    # 0.02 dB
        self._mo_spin = QDoubleSpinBox()
        self._mo_spin.setRange(-88.98, 167)
        self._mo_spin.setDecimals(2)
        self._mo_spin.setSingleStep(1.0)
        self._mo_spin.setValue(0.02)
        self._mo_spin.setSuffix(" dB")
        self._mo_slider.valueChanged.connect(
            lambda v: self._mo_spin.setValue(v - 88.98))
        self._mo_spin.valueChanged.connect(
            lambda v: self._mo_slider.setValue(max(0, min(255, round(v + 89)))))

        # --- Layout ---
        self._row_refs: list[tuple[QLabel, str, HelpButton]] = []
        container = QWidget()
        self._form = QFormLayout(container)
        self._add_row("drc.enable", self._enable_cb, "drc.enable")
        self._add_row("drc.threshold", _pair(self._thr_slider, self._thr_spin), "drc.threshold")
        self._add_row("drc.update_window", _pair(self._win_slider, self._win_spin), "drc.update_window")
        self._add_row("drc.window_extend", self._win_extend, "drc.window_extend")
        self._add_row("drc.attack", _pair(self._att_slider, self._att_spin), "drc.attack")
        self._form.addRow("", self._att_time_label)
        self._add_row("drc.release", _pair(self._rel_slider, self._rel_spin), "drc.release")
        self._form.addRow("", self._rel_time_label)
        self._add_row("drc.ratio", self._ratio_combo, "drc.ratio")
        self._add_row("drc.gain_compute", _pair(self._gc_slider, self._gc_spin), "drc.gain_compute")
        self._add_row("drc.noise_gate", _pair(self._ng_slider, self._ng_spin), "drc.noise_gate")
        self._add_row("drc.gain_balance", self._bal_combo, "drc.gain_balance")
        self._add_row("drc.makeup_gain", _pair(self._mu_slider, self._mu_spin), "drc.makeup_gain")
        self._add_row("drc.max_output", _pair(self._mo_slider, self._mo_spin), "drc.max_output")

        self.setWidget(container)

        # Initial time update
        self._update_times()

    def _add_row(self, key: str, widget: QWidget, help_key: str):
        lang = get_language()
        lbl = QLabel(tr(key, lang))
        help_btn = HelpButton(help_key, self)
        row = QWidget()
        layout = QHBoxLayout(row)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(lbl)
        layout.addWidget(help_btn)
        self._row_refs.append((lbl, key, help_btn))
        self._form.addRow(row, widget)

    def _on_win_extend(self, checked: bool) -> None:
        if checked:
            self._win_slider.setRange(0, 255)
            self._win_spin.setRange(0, 255)
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(self, tr("drc.window_extend", get_language()),
                                tr("drc.window_extend_warn", get_language()))
        else:
            if self._win_spin.value() < 96:
                self._win_spin.setValue(96)
            self._win_slider.setRange(96, 255)
            self._win_spin.setRange(96, 255)

    def _update_times(self) -> None:
        av = self._att_spin.value()
        rv = self._rel_spin.value()
        parts = []
        for fs in FS_VALUES:
            at = _attack_release_time(av, fs)
            rt = _attack_release_time(rv, fs)
            label = f"{fs//1000}k"
            if np.isfinite(at):
                parts.append(f"att@{label}={at:.1f}ms")
            else:
                parts.append(f"att@{label}=∞")
            if np.isfinite(rt):
                parts.append(f"rel@{label}={rt:.1f}ms")
            else:
                parts.append(f"rel@{label}=∞")
        self._att_time_label.setText("  ".join(parts[::2]))
        self._rel_time_label.setText("  ".join(parts[1::2]))

    @property
    def params(self) -> DRCParams:
        return DRCParams(
            threshold_db=self._thr_spin.value(),
            ratio_idx=self._ratio_combo.currentIndex(),
            attack_val=self._att_spin.value(),
            release_val=self._rel_spin.value(),
            update_window=self._win_spin.value(),
            gain_compute=self._gc_spin.value(),
            noise_gate_db=self._ng_spin.value(),
            gain_balance=self._bal_combo.currentIndex(),
            makeup_gain_db=self._mu_spin.value(),
            max_output_db=self._mo_spin.value(),
            extended_window=self._win_extend.isChecked(),
        )

    @property
    def enabled(self) -> bool:
        return self._enable_cb.isChecked()

    def set_enabled(self, enabled: bool) -> None:
        self._enable_cb.setChecked(enabled)

    def on_changed(self, slot) -> None:
        def _ch():
            self._update_times()
            slot()
        self._enable_cb.toggled.connect(lambda _: slot())
        self._thr_spin.valueChanged.connect(lambda _: slot())
        self._win_spin.valueChanged.connect(lambda _: slot())
        self._win_extend.toggled.connect(lambda _: slot())
        self._att_spin.valueChanged.connect(lambda _: _ch())
        self._rel_spin.valueChanged.connect(lambda _: _ch())
        self._ratio_combo.currentIndexChanged.connect(lambda _: slot())
        self._gc_spin.valueChanged.connect(lambda _: slot())
        self._ng_spin.valueChanged.connect(lambda _: slot())
        self._bal_combo.currentIndexChanged.connect(lambda _: slot())
        self._mu_spin.valueChanged.connect(lambda _: slot())
        self._mo_spin.valueChanged.connect(lambda _: slot())

    def refresh_language(self, lang: Lang) -> None:
        self._enable_cb.setText(tr("drc.enable", lang))
        for lbl, key, help_btn in self._row_refs:
            lbl.setText(tr(key, lang))
            help_btn.refresh_language(key)
        self._att_time_label.setText("")
        self._rel_time_label.setText("")
        self._update_times()
