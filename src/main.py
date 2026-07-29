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

import sys

from PySide6.QtWidgets import QApplication

from .adapters.designers.drc_hardware import HardwareDrcDesigner
from .adapters.designers.interpolating import load_coefficients
from .adapters.designers.rbj import RBJDesigner
from .adapters.gui.main_window import MainWindow
from .adapters.scripts.bat_formatter import BatScriptFormatter
from .application.drc_session import DRCSession
from .application.eq_session import EQSession
from .application.script_composer import ScriptComposer


def main() -> None:
    load_coefficients()
    eq_designer = RBJDesigner()
    drc_designer = HardwareDrcDesigner()
    formatter = BatScriptFormatter()

    eq_session = EQSession(eq_designer)
    drc_session = DRCSession()
    composer = ScriptComposer(eq_designer, drc_designer)

    app = QApplication(sys.argv)
    window = MainWindow(eq_session, drc_session, composer, formatter)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
