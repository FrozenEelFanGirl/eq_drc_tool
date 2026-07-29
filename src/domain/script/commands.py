from dataclasses import dataclass


@dataclass(frozen=True)
class RegisterWrite:
    """Value object: a single register write command."""

    address: int
    value: int
