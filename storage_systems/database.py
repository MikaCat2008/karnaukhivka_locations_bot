from aiosqlite import Cursor, Connection, connect

from engine.async_system import AsyncSystem


class DatabaseSystem(AsyncSystem):
    connection: Connection

    def __init__(self) -> None:
        super().__init__()

        self.connection = connect("database.db", isolation_level=None)

    async def execute(self, sql: str, *args) -> Cursor:
        return await self.connection.execute(sql, args)

    async def create_tables(self) -> None:
        await self.connection.executescript(
            """
                CREATE TABLE IF NOT EXISTS locations (
                    id INTEGER PRIMARY KEY,
                    name STRING,
                    files STRING,
                    likes INTEGER,
                    dislikes INTEGER,
                    verified BOOLEAN
                );

                CREATE TABLE IF NOT EXISTS pages (
                    text STRING,
                    location_id INTEGER
                );

                CREATE TABLE IF NOT EXISTS admin_sessions (
                    user_id INTEGER
                );
            """
        )

    async def async_start(self) -> None:
        await self.connection
        await self.create_tables()