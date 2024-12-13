from engine.async_system import AsyncSystem


class Storage_RatingSystem(AsyncSystem):
    async def like_location(self, user_id: int, location_id: int) -> None:
        ...

    async def unlike_location(self, user_id: int, location_id: int) -> None:
        ...

    async def dislike_location(self, user_id: int, location_id: int) -> None:
        ...

    async def undislike_location(self, user_id: int, location_id: int) -> None:
        ...
