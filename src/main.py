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
