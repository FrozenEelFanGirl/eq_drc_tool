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

from pathlib import Path

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QMainWindow,
    QMessageBox,
    QSplitter,
    QWidget,
)

from ...application.drc_session import DRCSession
from ...application.eq_session import EQSession
from ...application.ports import ScriptFormatter
from ...application.script_composer import ScriptComposer
from ...domain.eq.validity import check as check_validity
from ..scripts.config_io import export_config, import_config
from .drc_panel import DRCPanel
from .eq_panel import EQPanel
from .help_dialog import HelpDialog
from .copyright_dialog import CopyrightDialog
from .i18n import Lang, _, detect_os_language, set_language
from .plot_canvas import PlotCanvas


class MainWindow(QMainWindow):

    def __init__(self, eq_session: EQSession, drc_session: DRCSession,
                 composer: ScriptComposer, formatter: ScriptFormatter,
                 parent=None):
        super().__init__(parent)
        self._eq = eq_session
        self._drc = drc_session
        self._composer = composer
        self._formatter = formatter
        self._lang = detect_os_language()
        set_language(self._lang)

        self.setWindowTitle(_("app.title"))
        self.resize(1600, 900)

        self._refresh_timer = QTimer(singleShot=True, interval=50,
                                      timeout=self._do_refresh)
        self._build_menu()
        self._build_ui()
        self._wire_controls()
        self._do_refresh()

    # --- Menu ---
    def _build_menu(self) -> None:
        m = self.menuBar()

        file = m.addMenu(_("menu.file"))
        file.addAction(_("menu.file.import")).triggered.connect(lambda: self._import_config())
        file.addAction(_("menu.file.export")).triggered.connect(lambda: self._export_config())
        file.addSeparator()
        file.addAction(_("menu.file.export_bat")).triggered.connect(lambda: self._export_bat())
        file.addSeparator()
        file.addAction(_("menu.file.exit")).triggered.connect(self.close)

        lang_menu = m.addMenu(_("menu.language"))
        lang_menu.addAction(_("menu.lang.en")).triggered.connect(lambda: self._switch_lang(Lang.EN))
        lang_menu.addAction(_("menu.lang.zh")).triggered.connect(lambda: self._switch_lang(Lang.ZH))

        help_menu = m.addMenu(_("menu.help"))
        help_menu.addAction(_("menu.help.eq_guide")).triggered.connect(
            lambda: HelpDialog("eq_guide", self._lang, self).exec())
        help_menu.addAction(_("menu.help.drc_guide")).triggered.connect(
            lambda: HelpDialog("drc_guide", self._lang, self).exec())
        help_menu.addSeparator()
        help_menu.addAction(_("menu.help.about")).triggered.connect(
            lambda: CopyrightDialog(self._lang, self).exec())

    # --- Layout: EQ | DRC | Plot ---
    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)

        self._eq_panel = EQPanel()
        self._plot = PlotCanvas()
        self._drc_panel = DRCPanel()

        splitter = QSplitter()
        splitter.addWidget(self._eq_panel)
        splitter.addWidget(self._drc_panel)
        splitter.addWidget(self._plot)
        splitter.setStretchFactor(0, 6)
        splitter.setStretchFactor(1, 7)
        splitter.setStretchFactor(2, 7)

        layout = QHBoxLayout(central)
        layout.addWidget(splitter)

    # --- Controls ---
    def _wire_controls(self) -> None:
        def on_eq_changed():
            for i, strip in enumerate(self._eq_panel.strips):
                if strip.bypassed:
                    if not self._eq.bypass_flags[i]:
                        self._eq.toggle_band(i)
                else:
                    self._eq.update_band(i, strip.filter_params)
            self._debounce()

        for strip in self._eq_panel.strips:
            strip.on_changed(on_eq_changed)

        def on_drc_changed():
            self._drc.update(self._drc_panel.params)
            if self._drc.enabled != self._drc_panel.enabled:
                self._drc.toggle()
            self._debounce()
            self._plot.drc.update(self._drc_panel.params)

        self._drc_panel.on_changed(on_drc_changed)

    def _debounce(self) -> None:
        self._refresh_timer.start()

    def _do_refresh(self) -> None:
        designed = self._eq.active_coeffs()
        float_coeffs = [d.float_coeffs for d in designed]
        self._plot.mag.update(float_coeffs, self._eq.sample_rate)
        self._plot.phase.update(float_coeffs, self._eq.sample_rate)
        if self._drc.enabled:
            self._plot.drc.update(self._drc.params)

        for i, d in enumerate(designed):
            ok, err = check_validity(d.float_coeffs)
            self._eq_panel.strips[i].set_warning(
                _("eq.q_warn").format(i + 1, err) if not ok else None)

    # --- File operations ---
    def _export_bat(self) -> None:
        path, __ = QFileDialog.getSaveFileName(
            self, _("menu.file.export_bat"), "eq_drc_config.bat", _("config.filter"))
        if not path:
            return
        writes = self._composer.compose(self._eq, self._drc)
        Path(path).write_text(self._formatter.format(writes))
        QMessageBox.information(self, _("dialog.export_ok"),
                                _("dialog.export_ok_msg").format(path))

    def _export_config(self) -> None:
        try:
            default_path = str(Path.home() / "Desktop" / "eq_drc_config.json")
            path, __ = QFileDialog.getSaveFileName(
                self, _("menu.file.export"), default_path, _("config.json_filter"),
                options=QFileDialog.DontUseNativeDialog)
            if not path:
                return
            export_config(path, self._eq, self._drc)
            QMessageBox.information(self, _("dialog.export_ok"),
                                    _("dialog.export_ok_msg").format(path))
        except Exception as e:
            QMessageBox.warning(self, "Error",
                                f"Failed to export config:\n{type(e).__name__}: {e}")

    def _import_config(self) -> None:
        try:
            path, __ = QFileDialog.getOpenFileName(
                self, _("menu.file.import"), "", _("config.json_filter"))
            if not path:
                return
            import_config(path, self._eq, self._drc)
            self._sync_ui_from_session()
            self._do_refresh()
            QMessageBox.information(self, _("dialog.import_ok"),
                                    _("dialog.import_ok_msg").format(path))
        except Exception as e:
            QMessageBox.warning(self, _("config.import_error"),
                                _("config.import_error_msg").format(e))

    def _sync_ui_from_session(self) -> None:
        for i, strip in enumerate(self._eq_panel.strips):
            if not self._eq.bypass_flags[i] and self._eq.bands[i] is not None:
                strip.set_params(self._eq.bands[i])
            else:
                strip.set_bypassed()
        self._drc_panel.set_enabled(self._drc.enabled)

    # --- Language ---
    def _switch_lang(self, lang: Lang) -> None:
        self._lang = lang
        set_language(lang)
        self.setWindowTitle(_("app.title"))
        self.menuBar().clear()
        self._build_menu()
        self._eq_panel.refresh_language(lang)
        self._drc_panel.refresh_language(lang)
        self._plot.refresh_language()
