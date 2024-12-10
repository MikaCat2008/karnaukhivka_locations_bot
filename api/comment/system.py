from __future__ import annotations

from typing import TYPE_CHECKING

from core import System

if TYPE_CHECKING:
    from .entity import CommentEntity


class CommentSystem(System):
    def create_comment(self, text: str, author: str) -> CommentEntity:
        ...

    def edit_text(self, comment_id: int, text: str) -> None:
        ...

    def delete_comment(self, comment_id: int) -> None:
        ...
