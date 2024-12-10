from dataclasses import dataclass

from core import Component


@dataclass
class AdminComponent(Component):
    name: str
    role: str
