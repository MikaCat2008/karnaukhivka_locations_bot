from typing import Type, TypeVar, Generic, Optional
from asyncio import Lock

from engine.async_system import AsyncSystem

from .database import DatabaseSystem

K = TypeVar("K")
V = TypeVar("V")


class SafeDict(Generic[K, V]):
    _dict: dict[K, V]
    _lock: Lock
    _default: Type

    def __init__(self, default: Type = None):
        self._dict = {}
        self._lock = Lock()
        self._default = default

    def __getitem__(self, key: K) -> V:
        if key not in self._dict:
            if self._default:
                return self._default()
        else:
            return self._dict[key]

    def __contains__(self, key: K) -> bool:
        return key in self._dict

    async def set_value(self, key: K, value: V) -> None:
        async with self._lock:
            self._dict[key] = value

    async def del_key(self, key: K) -> None:
        async with self._lock:
            del self._dict[key]


class Storage_TelegramSystem(AsyncSystem):
    locations_ids: SafeDict[int, int]
    locations_lists: SafeDict[int, int]
    locations_file_ids: SafeDict[int, list[int]]
    locations_forwarded_ids: SafeDict[int, int]

    def __init__(self) -> None:
        super().__init__()

        self.locations_ids = SafeDict(int)
        self.locations_lists = SafeDict(int)
        self.locations_file_ids = SafeDict()
        self.locations_forwarded_ids = SafeDict()

    async def add_forwarded_message_id(self, message_id: int, location_id: int) -> None:
        database = DatabaseSystem()
        await database.execute(
            "INSERT INTO "
            "forwarded_messages(message_id, location_id)"
            "VALUES(?, ?)",
            message_id, location_id
        )    

    async def get_forwarded_message_id(self, location_id: int) -> Optional[int]:
        database = DatabaseSystem()
        async with await database.execute(
            "SELECT message_id FROM forwarded_messages WHERE location_id=?",
            location_id
        ) as cursor:
            row = await cursor.fetchone()

            if row:
                return row["message_id"]
