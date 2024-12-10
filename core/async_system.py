from core import System


class AsyncSystem(System):
    async def async_start(self) -> None:
        ...
