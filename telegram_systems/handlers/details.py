from aiogram import F
from aiogram.types import Message

from engine.async_system import AsyncSystem
from engine.aiogram_system import AiogramSystem

import consts


class Bot_DetailsHandlersSystem(AsyncSystem):
    async def on_details(self, message: Message) -> None:
        await message.answer(consts.TEXT_DETAILS)

    async def async_start(self) -> None:
        aiogram_system = AiogramSystem()

        dp = aiogram_system.dispatcher
        dp.message.register(self.on_details, F.text == consts.BUTTON_DETAILS)
