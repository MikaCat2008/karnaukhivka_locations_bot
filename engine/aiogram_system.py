from aiogram import Bot as AiogramBot, Dispatcher

from .async_system import AsyncSystem


class AiogramSystem(AsyncSystem):
    bots: dict[str, AiogramBot]
    dispatcher: Dispatcher

    def __init__(self) -> None:
        super().__init__()

        self.bots = {}
        self.dispatcher = Dispatcher()
        self.bot_entities = {}
    
    def add_bot(self, name: str, token: str) -> None:
        self.bots[name] = AiogramBot(token)

    async def async_start(self) -> None:
        await self.dispatcher.start_polling(*self.bots.values())
