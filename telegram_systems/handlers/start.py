from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from engine.async_system import AsyncSystem
from engine.aiogram_system import AiogramSystem

from storage_systems import Storage_AdminSystem
from telegram_systems.markups import Telegram_MarkupsSystem

import consts


class Bot_StartHandlersSystem(AsyncSystem):
    async def on_start(self, message: Message) -> None:
        storage_admin = Storage_AdminSystem()
        is_admin = await storage_admin.check_admin_session(
            message.from_user.id
        )

        markups = Telegram_MarkupsSystem()
        menu_markup = markups.get_menu_markup(is_admin)

        await message.answer(
            consts.TEXT_WELCOME, reply_markup=menu_markup
        )

    async def on_cancel(self, message: Message, state: FSMContext) -> None:
        await state.clear()

        storage_admin = Storage_AdminSystem()
        is_admin = await storage_admin.check_admin_session(
            message.from_user.id
        )

        markups = Telegram_MarkupsSystem()
        markup = markups.get_menu_markup(is_admin)

        await message.answer(
            consts.TEXT_CANCELLED, reply_markup=markup
        )

    async def async_start(self) -> None:
        aiogram_system = AiogramSystem()

        dp = aiogram_system.dispatcher
        dp.message.register(self.on_start, F.text == "/start")
        dp.message.register(self.on_cancel, F.text == consts.BUTTON_CANCEL)
