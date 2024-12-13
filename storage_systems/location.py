from typing import Iterable

from aiosqlite import Row

from engine.core import Entity
from engine.async_system import AsyncSystem

from components import (
    LocationComponent, 
    LocationFilesComponent, 
    LocationRatingComponent
)

from .database import DatabaseSystem

FILES_SEPARATOR = "::NEXT_FILE::"


class Storage_LocationSystem(AsyncSystem):
    def _get_rows(
        self, 
        files: bool = False,
        rating: bool = False
    ) -> list[str]:
        rows = ["id", "name"]

        if files:
            rows += ["files"]
        if rating:
            rows += ["likes", "dislikes"]
        
        return rows

    def _create_location(self, row: Row, rows: list[str]) -> Entity:
        entity = Entity()
        entity.add_component(
            LocationComponent(
                id=row["id"],
                name=row["name"]
            )
        )

        if "files" in rows:
            entity.add_component(
                LocationFilesComponent(
                    files=row["files"].split(FILES_SEPARATOR)
                )
            )
        if "likes" in rows:
            entity.add_component(
                LocationRatingComponent(
                    likes=row["likes"],
                    dislikes=row["dislikes"]
                )
            )

        return entity

    async def create_location(
        self, 
        name: str, 
        files: Iterable[str]    
    ) -> int:
        database = DatabaseSystem()
        async with await database.execute(
            "INSERT INTO "
            "locations(id, name, files, likes, dislikes, verified) "
            f"VALUES(NULL, ?, ?, ?, ?, FALSE)",
            name, 
            FILES_SEPARATOR.join(files), 
            0, 0
        ) as cursor:
            return cursor.lastrowid

    async def get_location(
        self, 
        location_id: int,
        files: bool = False,
        rating: bool = False
    ) -> Entity:
        rows = self._get_rows(files, rating)
        database = DatabaseSystem()

        async with await database.execute(
            f"SELECT {', '.join(rows)} FROM locations WHERE id=?",
            location_id
        ) as cursor:
            return self._create_location(
                await cursor.fetchone(), rows
            )
        
    async def get_locations(
        self,
        limit: int,
        offset: int,
        verify: bool,
        files: bool = False,
        rating: bool = False
    ) -> list[Entity]:
        rows = self._get_rows(files, rating)
        database = DatabaseSystem()

        async with await database.execute(
            f"SELECT {', '.join(rows)} "
            "FROM locations "
            f"WHERE verify={str(verify).capitalize()} "
            "LIMIT ? OFFSET ?",
            limit, offset
        ) as cursor:
            return [
                self._create_location(row)
                for row in await cursor.fetchall()
            ]

    async def verify_location(self, location_id: int) -> None:
        database = DatabaseSystem()
        await database.execute(
            "UPDATE locations SET verify=TRUE WHERE id=?",
            location_id
        )

    async def delete_location(self, location_id: int) -> None:
        database = DatabaseSystem()
        await database.execute(
            "DELETE FROM locations WHERE id=?",
            location_id
        )
