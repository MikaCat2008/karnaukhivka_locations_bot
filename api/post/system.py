from __future__ import annotations

from typing import TYPE_CHECKING
from collections import deque

from core import System

if TYPE_CHECKING:
    from .entity import PostEntity


class PostSystem(System):
    def create_post(self, text: str, media: deque[str]) -> PostEntity:
        ...

    def edit_text(self, post_id: int, text: str) -> None:
        ...

    def add_media(self, post_id: int, path: str) -> None:
        ...

    def delete_post(self, post_id: int) -> None:
        ...
