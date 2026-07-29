from typing import Protocol

from ..domain.script.commands import RegisterWrite


class ScriptFormatter(Protocol):
    """Port: format a list of register writes into a script string."""

    def format(self, writes: list[RegisterWrite]) -> str: ...


class Observer(Protocol):
    """Port: notified when session state changes."""

    def on_state_changed(self) -> None: ...
