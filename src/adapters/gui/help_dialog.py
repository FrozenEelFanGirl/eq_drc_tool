from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
)

from ..gui.i18n import Lang, tr

DOC_ROOT = Path(__file__).parent.parent.parent.parent / "doc" / "ref"
HELP_FILES = {
    "eq_guide": {
        Lang.EN: DOC_ROOT / "guildlines" / "EQ调试指南.md",
        Lang.ZH: DOC_ROOT / "guildlines" / "EQ调试指南.md",
    },
    "drc_guide": {
        Lang.EN: DOC_ROOT / "guildlines" / "DRC调试指南.md",
        Lang.ZH: DOC_ROOT / "guildlines" / "DRC调试指南.md",
    },
}


class HelpDialog(QDialog):
    """In-app help viewer with export button."""

    def __init__(self, doc_key: str, lang: Lang, parent=None):
        super().__init__(parent)
        self._doc_key = doc_key
        self._lang = lang
        self.setWindowTitle(tr(f"menu.help.{doc_key}", lang))
        self.resize(900, 600)

        self._text = QTextEdit()
        self._text.setReadOnly(True)
        self._text.setStyleSheet("font-family: 'Microsoft YaHei', sans-serif; font-size: 14px;")

        export_btn = QPushButton(tr("dialog.help_export", lang))
        export_btn.clicked.connect(self._export)

        layout = QVBoxLayout(self)
        layout.addWidget(self._text)
        layout.addWidget(export_btn)

        self._load()

    def _load(self) -> None:
        path = HELP_FILES[self._doc_key].get(self._lang) or list(HELP_FILES[self._doc_key].values())[0]
        try:
            text = path.read_text(encoding="utf-8")
            self._text.setMarkdown(text)
        except (OSError, UnicodeDecodeError):
            self._text.setPlainText(f"Could not load: {path}")

    def _export(self) -> None:
        from PySide6.QtWidgets import QFileDialog
        path, _ = QFileDialog.getSaveFileName(
            self, tr("menu.file.export", self._lang),
            f"{self._doc_key}.md",
            tr("config.md_filter", self._lang),
        )
        if path:
            src = HELP_FILES[self._doc_key].get(self._lang) or list(HELP_FILES[self._doc_key].values())[0]
            Path(path).write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
