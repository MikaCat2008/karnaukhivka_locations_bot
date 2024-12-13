from __future__ import annotations

from engine.singleton import Singleton


class System(Singleton):
    def start(self) -> None:
        ...
