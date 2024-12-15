from collections import deque

from aiogram import F
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from engine.async_system import AsyncSystem
from engine.aiogram_system import AiogramSystem

from storage_systems import (
    Storage_AdminSystem, 
    Storage_PagesSystem,
    Storage_LocationSystem
)
from telegram_systems.markups import Telegram_MarkupsSystem


class SuggestLocationForm(StatesGroup):
    location_name = State()
    location_pages = State()
    location_files = State()


class Bot_SuggestHandlersSystem(AsyncSystem):
    async def on_suggest(self, message: Message, state: FSMContext) -> None:
        await state.set_state(SuggestLocationForm.location_name)
        await state.update_data(
            location_pages_count=0,
            location_files_count=0
        )

        markups = Telegram_MarkupsSystem()
        markup = markups.get_cancel_markup()

        await message.answer(
            "Спочатку напишіть коротку назву локації. "
            "Якщо передумали, натисніть кнопку \"Скасувати\"",
            reply_markup=markup
        )
    
    async def set_location_name(self, message: Message, state: FSMContext) -> None:
        await state.update_data(
            location_name=message.text
        )
        await state.set_state(SuggestLocationForm.location_pages)

        markups = Telegram_MarkupsSystem()
        done_cancel_markup = markups.get_done_cancel_markup()

        await message.answer(
            "Тепер напишіть інформацію про локацію у "
            "такому форматі: скидуйте повідомлення("
            "розміром до 3000 символів), які будуть "
            "сторінками. Коли ви напишете всю "
            "інформацію, то натисніть на кнопку "
            "\"Все\".",
            reply_markup=done_cancel_markup
        )

    async def add_location_page(self, message: Message, state: FSMContext) -> None:
        text = message.text

        if len(message.text) > 3000:
            return await message.answer(
                "Довжина сторінки більша за 3000 символів"
                f"({len(message.text)}), тому вона не "
                "була зарахована."
            )

        pages_count: int = await state.get_value("location_pages_count")
        await state.update_data({
            "location_pages_count": pages_count + 1,
            f"location_page_{pages_count}": text
        })

    async def on_done_location_pages(self, message: Message, state: FSMContext) -> None:
        await state.set_state(SuggestLocationForm.location_files)

        markups = Telegram_MarkupsSystem()
        done_cancel_markup = markups.get_done_cancel_markup()

        await message.answer(
            "Наостанок можете надіслати декілька фото чи відео. "
            "Коли завершите, натисніть кнопку \"Все\".",
            reply_markup=done_cancel_markup
        )

    async def add_location_files(self, message: Message, state: FSMContext) -> None:
        files_count: int = await state.get_value("location_files_count")
        content_type: str = message.content_type

        if content_type == "photo":
            file_id = "photo_" + message.photo[0].file_id
        else:
            file_id = "video_" + message.video.file_id

        await state.update_data({
            "location_files_count": files_count + 1,
            f"location_file_id_{files_count}": file_id 
        })

    async def on_done_location_files(self, message: Message, state: FSMContext) -> None:
        data = await state.get_data()
        await state.clear()

        location_name: str = data["location_name"]
        location_pages: deque[str] = deque()
        location_files: deque[str] = deque()
        location_pages_count: int = data["location_pages_count"]
        location_files_count: int = data["location_files_count"]

        for i in range(location_pages_count):
            location_pages.append(
                data[f"location_page_{i}"]
            )

        for i in range(location_files_count):
            location_files.append(
                data[f"location_file_id_{i}"]
            )

        storage_location = Storage_LocationSystem()
        location_id = await storage_location.create_location(
            location_name, location_files
        )

        storage_pages = Storage_PagesSystem()
        await storage_pages.create_pages(location_pages, location_id)

        storage_admin = Storage_AdminSystem()
        is_admin = await storage_admin.check_admin_session(
            message.from_user.id
        )

        markups = Telegram_MarkupsSystem()
        menu_markup = markups.get_menu_markup(is_admin)

        await message.answer(
            "Дякуємо за внесок у нашого з Вами боту, цим Ви "
            "робите наше селище краще! Локація у найближчий "
            "час буде перевірена модераторами.",
            reply_markup=menu_markup
        )

    async def async_start(self) -> None:
        aiogram_system = AiogramSystem()

        dp = aiogram_system.dispatcher
        dp.message.register(self.on_suggest, F.text == "Запропонувати локацію")
        dp.message.register(
            self.set_location_name, 
            SuggestLocationForm.location_name
        )
        dp.message.register(
            self.on_done_location_pages, 
            F.text == "Все", 
            SuggestLocationForm.location_pages
        )
        dp.message.register(
            self.add_location_page, 
            SuggestLocationForm.location_pages
        )
        dp.message.register(
            self.on_done_location_files, 
            F.text == "Все", 
            SuggestLocationForm.location_files
        )
        dp.message.register(
            self.add_location_files, 
            F.photo | F.video,
            SuggestLocationForm.location_files
        )
