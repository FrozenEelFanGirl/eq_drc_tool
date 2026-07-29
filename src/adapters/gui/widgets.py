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

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QToolButton, QToolTip

from .i18n import get_language, tr


class HelpButton(QToolButton):
    """A '?' button that shows a tooltip on hover or click."""

    def __init__(self, help_key: str, parent=None):
        super().__init__(parent)
        self._tip = tr(f"help.{help_key}", get_language())
        self.setText("?")
        self.setStyleSheet(
            "QToolButton { border: none; color: #888; font-weight: bold;"
            " font-size: 11px; }"
        )

    def _show_tip(self):
        QToolTip.showText(
            self.mapToGlobal(self.rect().bottomLeft()), self._tip, self
        )

    def enterEvent(self, event):
        self._show_tip()
        super().enterEvent(event)

    def leaveEvent(self, event):
        QToolTip.hideText()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        self._show_tip()
        super().mousePressEvent(event)

    def refresh_language(self, help_key: str) -> None:
        self._tip = tr(f"help.{help_key}", get_language())


class LabelWithHelp(QLabel):
    """Label showing text with an embedded '?' indicator and tooltip on hover."""

    def __init__(self, key: str, parent=None):
        super().__init__(parent)
        self._key = key
        self._tip = ""
        self._refresh(get_language())
        self.setCursor(Qt.CursorShape.WhatsThisCursor)

    def _refresh(self, lang) -> None:
        text = tr(self._key, lang)
        self._tip = tr(f"help.{self._key}", lang)
        self.setText(f"{text} <span style='color:#888; font-weight:bold'>?</span>")

    def refresh_language(self, lang) -> None:
        self._refresh(lang)

    def enterEvent(self, event):
        QToolTip.showText(self.mapToGlobal(self.rect().bottomLeft()), self._tip, self)
        super().enterEvent(event)

    def leaveEvent(self, event):
        QToolTip.hideText()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        QToolTip.showText(self.mapToGlobal(self.rect().bottomLeft()), self._tip, self)
        super().mousePressEvent(event)
