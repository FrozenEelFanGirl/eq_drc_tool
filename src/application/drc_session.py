from ..domain.drc.params import DRCParams
from .ports import Observer

DEFAULT_DRC = DRCParams()


class DRCSession:
    """Observable state for DRC."""

    def __init__(self) -> None:
        self.params = DEFAULT_DRC
        self.enabled = False
        self._observers: list[Observer] = []

    # --- Observer ---
    def attach(self, observer: Observer) -> None:
        self._observers.append(observer)

    def detach(self, observer: Observer) -> None:
        self._observers.remove(observer)

    def _notify(self) -> None:
        for obs in self._observers:
            obs.on_state_changed()

    # --- Mutators ---
    def update(self, params: DRCParams) -> None:
        self.params = params
        self._notify()

    def toggle(self) -> None:
        self.enabled = not self.enabled
        self._notify()

    def disable(self) -> None:
        self.enabled = False
        self._notify()
