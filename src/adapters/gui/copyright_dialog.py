from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QDialog,
    QLabel,
    QTextEdit,
    QVBoxLayout,
)

from ..gui.i18n import Lang, tr

LOGO_PATH = Path(__file__).parent.parent.parent.parent / "doc" / "ref" / "copyright" / "company.png"

MIT_TEXT_EN = """MIT License

Copyright (c) 2026 FrozenEelFanGirl & Senary

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE."""

MIT_TEXT_ZH = """MIT 许可证

版权所有 (c) 2026 FrozenEelFanGirl & Senary

特此免费授予任何获得本软件及相关文档文件（以下简称"软件"）副本的人
不受限制地处理本软件的权利，包括但不限于使用、复制、修改、合并、出版、
分发、再许可和/或销售本软件副本的权利，但须符合以下条件：

上述版权声明和本许可声明应包含在本软件的所有副本或实质性部分中。

本软件按"原样"提供，不作任何明示或暗示的担保，包括但不限于对适销性、
特定用途适用性和非侵权的担保。在任何情况下，作者或版权持有人均不对
因本软件或本软件的使用或其他交易而产生的任何索赔、损害或其他责任负责，
无论是合同、侵权还是其他方式。"""

MIT_TEXTS = {Lang.EN: MIT_TEXT_EN, Lang.ZH: MIT_TEXT_ZH}


class CopyrightDialog(QDialog):
    """About / Copyright dialog with MIT license and logo."""

    def __init__(self, lang: Lang, parent=None):
        super().__init__(parent)
        self.setWindowTitle(tr("menu.help.about", lang))
        self.resize(600, 500)

        layout = QVBoxLayout(self)

        if LOGO_PATH.exists():
            logo = QLabel()
            pixmap = QPixmap(str(LOGO_PATH))
            scaled = pixmap.scaled(200, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo.setPixmap(scaled)
            logo.setAlignment(Qt.AlignCenter)
            layout.addWidget(logo)

        text = QTextEdit()
        text.setReadOnly(True)
        text.setPlainText(MIT_TEXTS.get(lang, MIT_TEXT_EN))
        text.setStyleSheet("font-family: 'Consolas', 'Microsoft YaHei', monospace; font-size: 12px;")
        layout.addWidget(text)
