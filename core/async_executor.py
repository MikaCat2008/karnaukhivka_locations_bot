from asyncio import Task, run as aio_run, create_task
from collections import deque

from .executor import Executor
from .async_system import AsyncSystem


class AsyncExecutor(Executor):
    async def async_start(self) -> None:
        tasks: deque[Task] = deque()

        for system in self.systems:
            if isinstance(system, AsyncSystem):
                task = create_task(system.async_start())
                tasks.append(task)

        for task in tasks:
            await task

    def start(self) -> None:
        super().start()

        aio_run(self.async_start())
