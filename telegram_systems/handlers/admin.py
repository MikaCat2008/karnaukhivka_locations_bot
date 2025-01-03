from aiogram import F
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from engine.async_system import AsyncSystem
from engine.aiogram_system import AiogramSystem

from storage_systems import Storage_AdminSystem
from telegram_systems.markups import Telegram_MarkupsSystem

import consts


class AdminLoginForm(StatesGroup):
    admin_name = State()
    admin_password = State()


class Bot_AdminHandlersSystem(AsyncSystem):
    async def on_exit(self, message: Message) -> None:
        storage_admin = Storage_AdminSystem()
        is_admin = await storage_admin.check_admin_session(
            message.from_user.id
        )

        if is_admin:
            await storage_admin.remove_admin_session(message.from_user.id)

            text = consts.TEXT_LOGOUT_ADMIN
        else:
            text = consts.TEXT_NOT_AUTHORIZED

        markups = Telegram_MarkupsSystem()
        menu_markup = markups.get_menu_markup(is_admin)

        await message.answer(text, reply_markup=menu_markup)

    async def on_admin(self, message: Message, state: FSMContext) -> None:
        storage_admin = Storage_AdminSystem()
        is_admin = await storage_admin.check_admin_session(
            message.from_user.id
        )

        if is_admin:
            await message.answer(
                consts.TEXT_ALREADY_AUTHORIZED
            )
        else:
            await state.set_state(AdminLoginForm.admin_name)
            await message.answer(consts.TEXT_ADMIN_AUTHORIZE_1)
    
    async def set_admin_name(self, message: Message, state: FSMContext) -> None:
        await state.set_state(AdminLoginForm.admin_password)
        await state.update_data(
            admin_name=message.text
        )
        await message.answer(consts.TEXT_ADMIN_AUTHORIZE_2)

    async def set_admin_password(self, message: Message, state: FSMContext) -> None:
        data = await state.get_data()
        await state.clear()

        admin_name: str = data["admin_name"]
        admin_password = message.text

        storage_admin = Storage_AdminSystem()
        status = await storage_admin.check_admin_data(
            admin_name, admin_password
        )

        if status:
            text = consts.TEXT_ADMIN_AUTHORIZED
        
            await storage_admin.add_admin_session(message.from_user.id)
        else:
            text = consts.TEXT_INCORRECT_ADMIN_DATA

        markups = Telegram_MarkupsSystem()
        menu_markup = markups.get_menu_markup(status)

        await message.answer(text, reply_markup=menu_markup)

    async def async_start(self) -> None:
        aiogram_system = AiogramSystem()

        dp = aiogram_system.dispatcher
        dp.message.register(self.on_exit, F.text == "/exit")
        dp.message.register(self.on_admin, F.text == "/admin")
        dp.message.register(self.set_admin_name, AdminLoginForm.admin_name)
        dp.message.register(self.set_admin_password, AdminLoginForm.admin_password)
