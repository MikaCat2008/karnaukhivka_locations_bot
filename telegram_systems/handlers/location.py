from typing import Optional
from collections import deque

from aiogram import F, Bot as TelegramBot
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    Message, CallbackQuery, InlineKeyboardMarkup,
    InputMedia, InputMediaPhoto, InputMediaVideo
)

from engine.core import Entity
from engine.async_system import AsyncSystem
from engine.aiogram_system import AiogramSystem

from components import (
    LocationComponent, 
    LocationFilesComponent,
    LocationRatingComponent
)
from storage_systems import (
    Storage_AdminSystem,
    Storage_PagesSystem,
    Storage_RatingSystem,
    Storage_LocationSystem,
    Storage_TelegramSystem
)
from telegram_systems.filters import admin_filter
from telegram_systems.markups import Telegram_MarkupsSystem


class CommentForm(StatesGroup):
    comment_text = State()


class Bot_LocationHandlersSystem(AsyncSystem):
    bot: TelegramBot

    # + location block

    async def _get_page(self, page_index: int, location_id: int) -> Optional[str]:
        storage_pages = Storage_PagesSystem()

        return await storage_pages.get_page(
            page_index, location_id
        )

    async def _get_rating(self, location: Entity) -> float:
        rating_component = location.get_component(LocationRatingComponent)
                
        likes = rating_component.likes
        dislikes = rating_component.dislikes

        if likes + dislikes == 0:
            return 5
        else:
            return round(5 * likes / (likes + dislikes), 1)

    async def _get_rating_markup(
        self, 
        index: int, 
        location: Entity,
        rate_value: Optional[bool] = None
    ) -> InlineKeyboardMarkup:
        identity_component = location.get_component(LocationComponent)
        location_id = identity_component.id

        rating_component = location.get_component(LocationRatingComponent)
        likes = rating_component.likes
        dislikes = rating_component.dislikes

        markups = Telegram_MarkupsSystem()

        storage_telegram = Storage_TelegramSystem()
        message_id = await storage_telegram.get_forwarded_message_id(location_id)

        return markups.get_rating_markup(index, likes, dislikes, message_id, rate_value)

    async def _get_location_text(self, location: Entity, page_index: int) -> str:
        identity_component = location.get_component(LocationComponent)
        rating = await self._get_rating(location)

        page_text = await self._get_page(
            page_index, identity_component.id
        )

        return (
            f"Назва: {identity_component.name}\n"
            f"Рейтинг: {rating} / 5\n\n" + 
            page_text
        )

    async def _get_unverified_location_text(self, location: Entity, page_index: int) -> str:
        identity_component = location.get_component(LocationComponent)

        page_text = await self._get_page(
            page_index, identity_component.id
        )

        return (
            "Запропонована локація:\n"
            f"Назва: {identity_component.name}\n\n" +
            page_text  
        )

    async def _get_locations(
        self, 
        message: Message, 
        verified: bool,
        index: int = None
    ) -> tuple[int, list[Entity]]:
        message_id = message.message_id

        if index is None:
            storage_telegram = Storage_TelegramSystem()
            index = storage_telegram.locations_lists[message_id]

        storage_location = Storage_LocationSystem()
        locations = await storage_location.get_locations(
            10, index * 10, verified, rating=verified
        )

        return index, locations

    async def _get_locations_data(
        self, 
        index: int, 
        verified: bool,
        locations: list[Entity]
    ) -> tuple[str, InlineKeyboardMarkup]:
        locations_data = deque()

        for location in locations:
            identity_component = location.get_component(LocationComponent)

            if verified:
                rating = await self._get_rating(location)

                text = f"{rating} | {identity_component.name}"
            else:
                text = identity_component.name

            locations_data.append((identity_component.id, text))

        if verified:
            text = f"Локації ({index * 10 + 1} - {index * 10 + len(locations)})"
        else:
            text = f"Запропоновані локації ({index * 10 + 1} - {index * 10 + len(locations)})"

        markups = Telegram_MarkupsSystem()
        markup = markups.get_locations_markup(
            index + 1, verified, locations_data
        )

        return text, markup

    async def send_locations(self, message: Message, verified: bool) -> None:
        _, locations = await self._get_locations(message, verified)
        
        text, locations_markup = await self._get_locations_data(
            0, verified, locations
        )
        message = await message.answer(
            text, reply_markup=locations_markup
        )

        storage_telegram = Storage_TelegramSystem()
        await storage_telegram.locations_lists.set_value(
            message.message_id, 0
        )

    async def flip_page(self, side: bool, message: Message, verified: bool) -> None:
        storage_telegram = Storage_TelegramSystem()
        index = storage_telegram.locations_lists[message.message_id]
        location_id = storage_telegram.locations_ids[message.message_id]
        new_index = index + side * 2 - 1

        page = await self._get_page(new_index, location_id)

        if side:
            if not page:
                return
        else:
            if index == 0:
                return
        
        await storage_telegram.locations_lists.set_value(
            message.message_id, new_index
        )
        
        await self.update_location(new_index, message, verified)

    async def update_location(
        self, 
        index: int,
        message: Message, 
        verified: bool
    ) -> None:
        storage_telegram = Storage_TelegramSystem()
        location_id = storage_telegram.locations_ids[message.message_id]

        storage_location = Storage_LocationSystem()
        location = await storage_location.get_location(
            location_id, True, verified
        )

        if verified:
            chat_id = message.chat.id
            
            storage_rating = Storage_RatingSystem()
            rate_value = await storage_rating.get_rate_value(
                chat_id, location_id
            )

            markup = await self._get_rating_markup(index + 1, location, rate_value)

            await message.edit_text(
                await self._get_location_text(location, index),
                reply_markup=markup
            )
        else:
            markups = Telegram_MarkupsSystem()
            markup = markups.get_verification_markup(index + 1)

            await message.edit_text(
                await self._get_unverified_location_text(location, index),
                reply_markup=markup
            )

    async def send_files(self, files: list[str], chat_id: int | str) -> list[Message]:
        files_data: deque[InputMedia] = deque()

        for file_id in files:
            content_type = file_id[:5]
            file_id = file_id[6:]

            if content_type == "photo":
                files_data.append(InputMediaPhoto(media=file_id))
            else:
                files_data.append(InputMediaVideo(media=file_id))

        return await self.bot.send_media_group(chat_id, files_data)

    async def update_locations(
        self, 
        index: int, 
        message: Message, 
        verified: bool,
        locations: list[Entity]
    ) -> None:
        text, locations_markup = await self._get_locations_data(index, verified, locations)

        await message.edit_text(
            text, reply_markup=locations_markup
        )

    async def flip_locations(self, side: bool, message: Message, verified: bool) -> None:
        storage_telegram = Storage_TelegramSystem()
        index = storage_telegram.locations_lists[message.message_id]
        new_index = index + side * 2 - 1

        _, locations = await self._get_locations(message, verified, index=new_index)
        
        if side:
            if not locations:
                return
        else:
            if index == 0:
                return
        
        await storage_telegram.locations_lists.set_value(
            message.message_id, new_index
        )
        await self.update_locations(
            new_index, message, verified, locations
        )

    async def send_location(
        self, 
        message: Message, 
        verified: bool, 
        location_id: int
    ) -> None:
        storage_location = Storage_LocationSystem()
        location = await storage_location.get_location(
            location_id, True, verified
        )

        files_component = location.get_component(LocationFilesComponent)
        files = files_component.files

        if files:
            file_ids = [
                message.message_id
                for message in await self.send_files(files, message.chat.id)
            ]
        else:
            file_ids = []

        if verified:
            chat_id = message.chat.id

            storage_rating = Storage_RatingSystem()
            rate_value = await storage_rating.get_rate_value(
                chat_id, location_id
            )

            markup = await self._get_rating_markup(1, location, rate_value)
        else:
            markups = Telegram_MarkupsSystem()
            markup = markups.get_verification_markup(1)

        if verified:
            message = await message.answer(
                await self._get_location_text(location, 0),
                reply_markup=markup
            )
        else:
            message = await message.answer(
                await self._get_unverified_location_text(location, 0),
                reply_markup=markup
            )

        storage_telegram = Storage_TelegramSystem()

        await storage_telegram.locations_ids.set_value(
            message.message_id, location_id
        )
        await storage_telegram.locations_lists.set_value(
            message.message_id, 0
        )
        await storage_telegram.locations_file_ids.set_value(
            message.message_id, file_ids
        )

    async def on_location(self, callback: CallbackQuery) -> None:
        await self.send_location(
            callback.message, True, int(callback.data[9:])
        )

    async def on_unverified_location(self, callback: CallbackQuery) -> None:
        await self.send_location(
            callback.message, False, int(callback.data[20:])
        )

    async def rate(self, value: bool, message: Message) -> None:
        chat_id = message.chat.id
        message_id = message.message_id

        storage_telegram = Storage_TelegramSystem()
        location_id = storage_telegram.locations_ids[message_id]

        storage_rating = Storage_RatingSystem()
        stored_value = await storage_rating.get_rate_value(chat_id, location_id)

        storage_location = Storage_LocationSystem()

        if stored_value is None:
            await storage_rating.add_rate_value(value, chat_id, location_id)
            await storage_location.add_rating(value, location_id)
        elif value == stored_value:
            await storage_rating.delete_rate_value(chat_id, location_id)
            await storage_location.remove_rating(value, location_id)
        elif value != stored_value:
            await storage_rating.update_rate_value(value, chat_id, location_id)
            await storage_location.add_rating(value, location_id)
            await storage_location.remove_rating(not value, location_id)

        index = storage_telegram.locations_lists[message_id]

        await self.update_location(index, message, True)

    async def on_like_location(self, callback: CallbackQuery) -> None:
        await self.rate(True, callback.message)

    async def on_dislike_location(self, callback: CallbackQuery) -> None:
        await self.rate(False, callback.message)

    async def on_comment_location(self, callback: CallbackQuery, state: FSMContext) -> None:
        message = callback.message
        message_id = message.message_id
        
        storage_telegram = Storage_TelegramSystem()
        location_id = storage_telegram.locations_ids[message_id]

        await state.set_state(CommentForm.comment_text)
        await state.update_data(
            location_id=location_id
        )

        markups = Telegram_MarkupsSystem()
        markup = markups.get_cancel_markup()

        await message.answer(
            "Напишіть Ваше враження про локацію.",
            reply_markup=markup
        )

    async def get_comment_text(self, message: Message, state: FSMContext) -> None:
        storage_admin = Storage_AdminSystem()
        is_admin = await storage_admin.check_admin_session(
            message.from_user.id
        )

        markups = Telegram_MarkupsSystem()
        markup = markups.get_menu_markup(is_admin)

        await message.answer(
            "Дякуємо за допомогу! Ваш відгук може повпливати "
            "на опис.",
            reply_markup=markup
        )

        storage_telegram = Storage_TelegramSystem()
        message_id = await storage_telegram.get_forwarded_message_id(
            await state.get_value("location_id")
        )

        await state.clear()
        await self.bot.send_message(
            "@karnaukhivka_locations_chat",
            f"Анонімний відгук: {message.text}",
            reply_to_message_id=message_id
        )

    async def on_hide_location(self, callback: CallbackQuery) -> None:
        message = callback.message
        chat_id = message.chat.id
        message_id = message.message_id

        storage_telegram = Storage_TelegramSystem()
        file_ids = storage_telegram.locations_file_ids[message_id]
        
        await self.bot.delete_messages(chat_id, file_ids + [message_id])

    async def on_deny_location(self, callback: CallbackQuery) -> None:
        message = callback.message
        chat_id = message.chat.id
        message_id = message.message_id

        storage_telegram = Storage_TelegramSystem()
        file_ids = storage_telegram.locations_file_ids[message_id]
        location_id = storage_telegram.locations_ids[message_id]

        storage_location = Storage_LocationSystem()
        await storage_location.delete_location(location_id)
        
        storage_pages = Storage_PagesSystem()
        await storage_pages.delete_pages(location_id)

        await self.bot.delete_messages(chat_id, file_ids + [message_id])

    async def on_verify_location(self, callback: CallbackQuery) -> None:
        message = callback.message
        message_id = message.message_id

        storage_telegram = Storage_TelegramSystem()
        location_id = storage_telegram.locations_ids[message_id]

        storage_location = Storage_LocationSystem()
        await storage_location.verify_location(location_id)

        markups = Telegram_MarkupsSystem()
        markup = markups.get_menu_markup(True)

        await message.answer(
            "Локація опублікована. Дякуємо за співпрацю!",
            reply_markup=markup
        )

        storage_location = Storage_LocationSystem()
        location = await storage_location.get_location(
            location_id, True, False
        )

        files_component = location.get_component(LocationFilesComponent)
        files = files_component.files

        if files:
            await self.send_files(files, "@karnaukhivka_locations")

        identity_component = location.get_component(LocationComponent)
        name = identity_component.name

        message = await self.bot.send_message(
            "@karnaukhivka_locations", 
            f"Нова локація: {name}"
        )

        await storage_telegram.locations_forwarded_ids.set_value(
            message.message_id, location_id
        )

    async def on_left_location(self, callback: CallbackQuery) -> None:
        await self.flip_page(False, callback.message, True)

    async def on_right_location(self, callback: CallbackQuery) -> None:
        await self.flip_page(True, callback.message, True)

    async def on_left_unverified_location(self, callback: CallbackQuery) -> None:
        await self.flip_page(False, callback.message, False)

    async def on_right_unverified_location(self, callback: CallbackQuery) -> None:
        await self.flip_page(True, callback.message, False)

    # - location block
    # + locations block 

    async def on_locations(self, message: Message) -> None:        
        await self.send_locations(message, True)

    async def on_check_locations(self, message: Message) -> None:        
        await self.send_locations(message, False)

    async def on_left_locations(self, callback: CallbackQuery) -> None:
        await self.flip_locations(False, callback.message, True)

    async def on_right_locations(self, callback: CallbackQuery) -> None:
        await self.flip_locations(True, callback.message, True)

    async def on_left_unverified_locations(self, callback: CallbackQuery) -> None:
        await self.flip_locations(False, callback.message, False)

    async def on_right_unverified_locations(self, callback: CallbackQuery) -> None:
        await self.flip_locations(True, callback.message, False)

    async def on_forward(self, message: Message) -> None:
        message_id = message.message_id
        forwarded_message_id = message.forward_from_message_id

        storage_telegram = Storage_TelegramSystem()
        location_id = storage_telegram.locations_forwarded_ids[forwarded_message_id]

        if location_id is None:
            return await message.delete()
        
        await storage_telegram.locations_forwarded_ids.del_key(forwarded_message_id)
        await storage_telegram.add_forwarded_message_id(
            message_id, location_id
        )

    # - locations block

    async def async_start(self) -> None:
        aiogram_system = AiogramSystem()

        dp = aiogram_system.dispatcher

        dp.message.register(self.on_locations, F.text == "Локації")
        dp.message.register(
            self.on_check_locations, 
            F.text == "Перевірити локації",
            admin_filter
        )

        dp.callback_query.register(
            self.on_location, F.data.startswith("location")
        )
        dp.callback_query.register(
            self.on_unverified_location, 
            F.data.startswith("unverified_location")
        )

        dp.callback_query.register(
            self.on_deny_location, 
            F.data == "deny_location"
        )
        dp.callback_query.register(
            self.on_verify_location, 
            F.data == "verify_location"
        )
        
        dp.callback_query.register(
            self.on_like_location, F.data == "like_location"
        )
        dp.callback_query.register(
            self.on_dislike_location, F.data == "dislike_location"
        )
        dp.callback_query.register(
            self.on_comment_location, F.data == "comment_location"
        )
        dp.message.register(
            self.get_comment_text, CommentForm.comment_text
        )
        dp.callback_query.register(
            self.on_hide_location, F.data == "hide_location"
        )

        dp.callback_query.register(
            self.on_left_location, F.data == "left_location"
        )
        dp.callback_query.register(
            self.on_right_location, F.data == "right_location"
        )
        dp.callback_query.register(
            self.on_left_unverified_location, F.data == "left_unverified_location"
        )
        dp.callback_query.register(
            self.on_right_unverified_location, F.data == "right_unverified_location"
        )

        dp.callback_query.register(
            self.on_left_locations, F.data == "left_locations"
        )
        dp.callback_query.register(
            self.on_right_locations, F.data == "right_locations"
        )
        dp.callback_query.register(
            self.on_left_unverified_locations, 
            F.data == "left_unverified_locations"
        )
        dp.callback_query.register(
            self.on_right_unverified_locations, 
            F.data == "right_unverified_locations"
        )

        dp.message.register(self.on_forward, F.from_user.id == 777000)

        self.bot = aiogram_system.bots["karnaukhivka_locations_bot"]
