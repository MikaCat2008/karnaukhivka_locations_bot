from .core import System


class Executor:
    systems: list[System]

    def __init__(self, systems: list[System]) -> None:
        self.systems = systems

    def start(self) -> None:
        for system in self.systems:
            system.executor = self

        for system in self.systems:
            system.start()
