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
