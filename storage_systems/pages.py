from typing import Iterable, Optional

from engine.core import Entity
from engine.async_system import AsyncSystem

from .database import DatabaseSystem


class Storage_PagesSystem(AsyncSystem):
    async def create_pages(self, pages: Iterable[str], location_id: int) -> None:
        database = DatabaseSystem()
        
        await database.execute(
            "INSERT INTO pages(text, location_id) "
            f"VALUES{', '.join([f'(?, {location_id})'] * len(pages))}",
            *pages
        )

    async def get_page(self, page_index: int, location_id: int) -> Optional[str]:
        database = DatabaseSystem()
        async with await database.execute(
            "SELECT text FROM pages WHERE location_id=? LIMIT 1 OFFSET ?",
            location_id, page_index
        ) as cursor:
            row = await cursor.fetchone()
            
            if row:
                return row["text"]

    async def edit_page(
        self, 
        text: str,
        page_index: int,
        location_id: int
    ) -> Entity:
        database = DatabaseSystem()

        await database.execute(
            "UPDATE pages SET text=? WHERE rowid=? AND location_id=?",
            text, page_index, location_id
        )

    async def delete_page(
        self, 
        page_index: int,
        location_id: int
    ) -> Entity:
        database = DatabaseSystem()
        await database.execute(
            "DELETE FROM pages WHERE rowid=? AND location_id=?",
            page_index, location_id
        )

    async def delete_pages(self, location_id: int) -> None:
        database = DatabaseSystem()
        await database.execute(
            "DELETE FROM pages WHERE location_id=?",
            location_id
        )
