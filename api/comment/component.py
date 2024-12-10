from dataclasses import dataclass

from core import Component


@dataclass
class CommentComponent(Component):
    id: int
    text: str
    author: str
