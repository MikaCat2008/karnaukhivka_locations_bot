from typing import Optional

from engine.async_system import AsyncSystem

from .database import DatabaseSystem


class Storage_RatingSystem(AsyncSystem):
    async def get_rate_value(self, user_id: int, location_id: int) -> Optional[bool]:
        database = DatabaseSystem()
    
        async with await database.execute(
            "SELECT value FROM ratings WHERE user_id=? AND location_id=?",
            user_id, location_id
        ) as cursor:
            row = await cursor.fetchone()

            if row:
                return row["value"]

    async def add_rate_value(self, value: bool, user_id: int, location_id: int) -> None:
        database = DatabaseSystem()

        await database.execute(
            "INSERT INTO ratings(value, user_id, location_id) "
            "VALUES(?, ?, ?)",
            value, user_id, location_id
        )

    async def update_rate_value(self, value: bool, user_id: int, location_id: int) -> None:
        database = DatabaseSystem()

        await database.execute(
            "UPDATE ratings SET value=? WHERE user_id=? AND location_id=?",
            value, user_id, location_id
        )

    async def delete_rate_value(self, user_id: int, location_id: int) -> None:
        database = DatabaseSystem()

        await database.execute(
            "DELETE FROM ratings WHERE user_id=? AND location_id=?",
            user_id, location_id
        )
