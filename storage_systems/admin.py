from engine.async_system import AsyncSystem

from .database import DatabaseSystem

from config import ADMIN_NAME, ADMIN_PASSWORD


class Storage_AdminSystem(AsyncSystem):    
    async def add_admin_session(self, user_id: int) -> None:
        database = DatabaseSystem()
        await database.execute(
            "INSERT INTO admin_sessions(user_id) VALUES(?)",
            user_id
        )

    async def check_admin_session(self, user_id: int) -> bool:
        database = DatabaseSystem()
        async with await database.execute(
            "SELECT * FROM admin_sessions WHERE user_id=?",
            user_id
        ) as cursor:
            row = await cursor.fetchone()
            
            return row is not None

    async def remove_admin_session(self, user_id: int) -> None:
        database = DatabaseSystem()
        await database.execute(
            "DELETE FROM admin_sessions WHERE user_id=?",
            user_id
        )

    async def check_admin_data(self, name: str, password: str) -> bool:
        return name == ADMIN_NAME and password == ADMIN_PASSWORD
