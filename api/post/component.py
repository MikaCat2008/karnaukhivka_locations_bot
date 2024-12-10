from collections import deque
from dataclasses import dataclass

from core import Component


@dataclass
class PostComponent(Component):
    id: int
    text: str
    media: deque[str]
