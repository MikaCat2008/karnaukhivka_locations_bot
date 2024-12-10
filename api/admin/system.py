from __future__ import annotations

from typing import Optional, TYPE_CHECKING

from core import System

if TYPE_CHECKING:
    from .entity import AdminEntity


class AdminSystem(System):
    def get_admin_entity(self, name: str) -> Optional[AdminEntity]:
        ...

    def promote(self, name: str, role: str) -> AdminEntity:
        ...

    def demote(self, name: str) -> None:
        ...
