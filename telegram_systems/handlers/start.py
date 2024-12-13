from aiogram import F
from aiogram.types import Message

from engine.async_system import AsyncSystem
from engine.aiogram_system import AiogramSystem

from storage_systems import Storage_AdminSystem
from telegram_systems.markups import Telegram_MarkupsSystem


class Bot_StartHandlersSystem(AsyncSystem):
    async def on_start(self, message: Message) -> None:
        storage_admin = Storage_AdminSystem()
        is_admin = await storage_admin.check_admin_session(
            message.from_user.id
        )

        markups = Telegram_MarkupsSystem()
        menu_markup = markups.get_menu_markup(is_admin)

        await message.answer(
            "Я - бот, створений для допомоги жителям селища Карнаухівка. "
            "Для подробиць тисніть кнопку \"Детальніше\".",
            reply_markup=menu_markup
        )

    async def async_start(self) -> None:
        aiogram_system = AiogramSystem()

        dp = aiogram_system.dispatcher
        dp.message.register(self.on_start, F.text == "/start")
