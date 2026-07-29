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

import pyqtgraph as pg
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import (
    QCheckBox, QHBoxLayout, QTabWidget, QVBoxLayout, QWidget,
)

from ...domain.drc.params import DRCParams
from ...domain.drc.transfer_curve import evaluate as drc_curve
from ...domain.eq.coefficients import BiquadCoefficients
from ...domain.eq.frequency_response import (
    evaluate_per_band,
    evaluate_phase,
    evaluate_phase_per_band,
    evaluate_quantized_phase,
    evaluate_quantized_response,
)
from ..gui.i18n import _ as tr


def _make_vb(plot: pg.PlotWidget):
    return plot.getPlotItem().vb


def _fix_x(plot: pg.PlotWidget, log_x: bool) -> None:
    vb = _make_vb(plot)
    vb.disableAutoRange(axis=pg.ViewBox.XAxis)
    if log_x:
        import numpy as np
        vb.setXRange(np.log10(0.02), np.log10(20.0), padding=0)
    else:
        vb.setXRange(0.0, 20.0, padding=0)


def _fix_y(plot: pg.PlotWidget, ymin: float, ymax: float) -> None:
    vb = _make_vb(plot)
    vb.disableAutoRange(axis=pg.ViewBox.YAxis)
    vb.setLimits(yMin=ymin, yMax=ymax)
    vb.setYRange(ymin, ymax, padding=0)


def _auto_y(plot: pg.PlotWidget) -> None:
    vb = _make_vb(plot)
    vb.setLimits(yMin=None, yMax=None, minYRange=None, maxYRange=None)
    vb.enableAutoRange(axis=pg.ViewBox.YAxis, enable=True)
    vb.autoRange()


def _build_checkboxes(labels_key: str, count: int):
    cbs = []
    for i in range(count):
        cb = QCheckBox(tr(labels_key).format(i + 1))
        cb.setChecked(False)
        cbs.append(cb)
    return cbs


def _checkbox_row(checkboxes: list[QCheckBox]) -> QWidget:
    row = QWidget()
    layout = QHBoxLayout(row)
    layout.setContentsMargins(0, 0, 0, 0)
    for cb in checkboxes:
        layout.addWidget(cb)
    layout.addStretch()
    return row


def _def_pen(color, width=2, style=pg.QtCore.Qt.SolidLine):
    return pg.mkPen(color=color, width=width, style=style)


# --- Tabs ---

class MagTab(QWidget):
    Y_MIN, Y_MAX = -12, 12

    def __init__(self, parent=None):
        super().__init__(parent)

        self.plot = pg.PlotWidget(title=tr("plot.magnitude"))
        self.plot.setLabel("bottom", tr("plot.frequency_khz"))
        self.plot.setLabel("left", tr("plot.magnitude_db"))
        self.plot.setLogMode(x=False)
        self.plot.showGrid(x=True, y=True)
        _fix_y(self.plot, self.Y_MIN, self.Y_MAX)

        pi = self.plot.getPlotItem()
        pi.ctrl.logXCheck.toggled.connect(lambda v: (_fix_x(self.plot, v), _fix_y(self.plot, self.Y_MIN, self.Y_MAX)))
        QTimer.singleShot(0, lambda: _fix_x(self.plot, False))

        self.cascade = self.plot.plot(pen=_def_pen((0, 120, 255)))
        self.float_curve = self.plot.plot(pen=_def_pen((0, 180, 0), style=pg.QtCore.Qt.DashLine))
        self.float_curve.setVisible(False)

        self.band_curves = []
        colors = [(255, 100, 100), (100, 255, 100), (100, 100, 255),
                  (255, 255, 100), (255, 100, 255), (100, 255, 255), (200, 150, 100)]
        for c in colors:
            curve = self.plot.plot(pen=_def_pen(c, width=1, style=pg.QtCore.Qt.DashLine))
            curve.setVisible(False)
            self.band_curves.append(curve)

        # --- controls ---
        self._band_cbs = _build_checkboxes("plot.show_band", 7)
        for i, cb in enumerate(self._band_cbs):
            cb.toggled.connect(lambda v, idx=i: self.band_curves[idx].setVisible(v))

        self._diff_cb = QCheckBox(tr("plot.show_float_vs_q"))
        self._diff_cb.setChecked(False)
        self._diff_cb.toggled.connect(self.float_curve.setVisible)

        controls = QVBoxLayout()
        controls.addWidget(_checkbox_row(self._band_cbs))
        controls.addWidget(self._diff_cb)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addLayout(controls)
        layout.addWidget(self.plot)

    def update(self, coefficients: list[BiquadCoefficients], sample_rate: int) -> None:
        freqs, mag_float, mag_quant = evaluate_quantized_response(coefficients, sample_rate)
        f = freqs / 1000.0
        self.cascade.setData(f, mag_quant)
        self.float_curve.setData(f, mag_float)

        _, band_mags = evaluate_per_band(coefficients, sample_rate)
        for i, mag in enumerate(band_mags):
            self.band_curves[i].setData(f, mag)

    def set_band_visible(self, idx: int, v: bool) -> None:
        self._band_cbs[idx].setChecked(v)
        self.band_curves[idx].setVisible(v)

    def refresh_language(self) -> None:
        self.plot.setTitle(tr("plot.magnitude"))
        self.plot.setLabel("bottom", tr("plot.frequency_khz"))
        self.plot.setLabel("left", tr("plot.magnitude_db"))
        for i, cb in enumerate(self._band_cbs):
            cb.setText(tr("plot.show_band").format(i + 1))
        self._diff_cb.setText(tr("plot.show_float_vs_q"))


class PhaseTab(QWidget):
    Y_MIN, Y_MAX = -180, 180

    def __init__(self, parent=None):
        super().__init__(parent)

        self.plot = pg.PlotWidget(title=tr("plot.phase"))
        self.plot.setLabel("bottom", tr("plot.frequency_khz"))
        self.plot.setLabel("left", tr("plot.phase_deg"))
        self.plot.setLogMode(x=False)
        self.plot.showGrid(x=True, y=True)
        _fix_y(self.plot, self.Y_MIN, self.Y_MAX)

        pi = self.plot.getPlotItem()
        pi.ctrl.logXCheck.toggled.connect(lambda v: (_fix_x(self.plot, v), _fix_y(self.plot, self.Y_MIN, self.Y_MAX)))
        QTimer.singleShot(0, lambda: _fix_x(self.plot, False))

        self.cascade = self.plot.plot(pen=_def_pen((0, 120, 255)))
        self.float_curve = self.plot.plot(pen=_def_pen((0, 180, 0), style=pg.QtCore.Qt.DashLine))
        self.float_curve.setVisible(False)

        self.band_curves = []
        colors = [(255, 100, 100), (100, 255, 100), (100, 100, 255),
                  (255, 255, 100), (255, 100, 255), (100, 255, 255), (200, 150, 100)]
        for c in colors:
            curve = self.plot.plot(pen=_def_pen(c, width=1, style=pg.QtCore.Qt.DashLine))
            curve.setVisible(False)
            self.band_curves.append(curve)

        # --- controls ---
        self._band_cbs = _build_checkboxes("plot.show_band", 7)
        for i, cb in enumerate(self._band_cbs):
            cb.toggled.connect(lambda v, idx=i: self.band_curves[idx].setVisible(v))

        self._diff_cb = QCheckBox(tr("plot.show_float_vs_q"))
        self._diff_cb.setChecked(False)
        self._diff_cb.toggled.connect(self.float_curve.setVisible)

        controls = QVBoxLayout()
        controls.addWidget(_checkbox_row(self._band_cbs))
        controls.addWidget(self._diff_cb)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addLayout(controls)
        layout.addWidget(self.plot)

    def update(self, coefficients: list[BiquadCoefficients], sample_rate: int) -> None:
        freqs, phase_float, phase_quant = evaluate_quantized_phase(coefficients, sample_rate)
        f = freqs / 1000.0
        self.cascade.setData(f, phase_quant)
        self.float_curve.setData(f, phase_float)

        _, band_phases = evaluate_phase_per_band(coefficients, sample_rate)
        for i, ph in enumerate(band_phases):
            self.band_curves[i].setData(f, ph)

    def refresh_language(self) -> None:
        self.plot.setTitle(tr("plot.phase"))
        self.plot.setLabel("bottom", tr("plot.frequency_khz"))
        self.plot.setLabel("left", tr("plot.phase_deg"))
        for i, cb in enumerate(self._band_cbs):
            cb.setText(tr("plot.show_band").format(i + 1))
        self._diff_cb.setText(tr("plot.show_float_vs_q"))


class DrcTab(QWidget):
    Y_MIN, Y_MAX = -80, 36

    def __init__(self, parent=None):
        super().__init__(parent)
        self.plot = pg.PlotWidget(title=tr("plot.drc"))
        self.plot.setLabel("bottom", tr("plot.input_db"))
        self.plot.setLabel("left", tr("plot.output_db"))
        self.plot.showGrid(x=True, y=True)
        _fix_y(self.plot, self.Y_MIN, self.Y_MAX)

        self.curve = self.plot.plot(pen=_def_pen((255, 120, 0)))
        self.ref = self.plot.plot(pen=_def_pen((128, 128, 128), width=1,
                                               style=pg.QtCore.Qt.DashLine))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.plot)

    def update(self, params: DRCParams) -> None:
        in_db, out_db = drc_curve(params)
        self.curve.setData(in_db, out_db)
        self.ref.setData(in_db, in_db)

    def refresh_language(self) -> None:
        self.plot.setTitle(tr("plot.drc"))
        self.plot.setLabel("bottom", tr("plot.input_db"))
        self.plot.setLabel("left", tr("plot.output_db"))


# --- Container ---

class PlotCanvas(QWidget):
    """Three-tab plot: Magnitude | Phase | DRC."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.mag = MagTab()
        self.phase = PhaseTab()
        self.drc = DrcTab()

        self._tabs = QTabWidget()
        self._tabs.addTab(self.mag, tr("plot.magnitude"))
        self._tabs.addTab(self.phase, tr("plot.phase"))
        self._tabs.addTab(self.drc, tr("plot.drc"))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._tabs)

    def refresh_language(self) -> None:
        self.mag.refresh_language()
        self.phase.refresh_language()
        self.drc.refresh_language()
        self._tabs.setTabText(0, tr("plot.magnitude"))
        self._tabs.setTabText(1, tr("plot.phase"))
        self._tabs.setTabText(2, tr("plot.drc"))
