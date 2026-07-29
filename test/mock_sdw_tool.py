from dataclasses import dataclass


@dataclass
class MockSdwTool:
    """Fake SdwRegisterTool.exe for offline testing."""

    read_responses: dict[int, int]
    writes: list[tuple[int, int]]

    def __init__(self):
        self.read_responses = {}
        self.writes = []

    def set_read_response(self, address: int, value: int) -> None:
        self.read_responses[address] = value

    def run(self, args: list[str]) -> str:
        """Simulate running SdwRegisterTool.exe with given args.

        Args:
            args: e.g. ['w', 'reg', '2065', '93'] or ['r', 'reg', '2060']

        Returns:
            Output string in .exe format.
        """
        if args[0] == "w":
            addr = int(args[2], 16)
            val = int(args[3], 16)
            self.writes.append((addr, val))
            return f"Address={addr:04X} Value={val:02X} Status=00000000\r\n"

        elif args[0] == "r":
            addr = int(args[2], 16)
            val = self.read_responses.get(addr, 0)
            return f"Address={addr:04X} Value={val:02X} Status=00000000\r\n"

        else:
            return "Address=0000 Value=00 Status=00000001\r\n"

    def simulate_failure(self, address: int) -> str:
        """Return a failure response for a given address."""
        return f"Address={address:04X} Value=00 Status=00000001\r\n"
