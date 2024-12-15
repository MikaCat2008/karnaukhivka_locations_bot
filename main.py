from engine.async_executor import AsyncExecutor
from engine.aiogram_system import AiogramSystem

from storage_systems import SYSTEMS as STORAGE_SYSTEMS
from telegram_systems import SYSTEMS as TELEGRAM_SYSTEMS

from config import TOKEN


# class Bot_ViewLocationSystem(AsyncSystem):
#     bot: TelegramBot

#     async def update_location_by_id(self, message: Message, location_id: int) -> None:
#         database = DatabaseSystem()
        
#         await self.update_location(
#             message, await database.get_location(location_id)
#         )

#     async def on_hide(self, callback: CallbackQuery) -> None:
#         message = callback.message
#         location_id = int(callback.data[4:])

#         chat_id = message.chat.id

#         message_link = MessageLinkSystem()
#         message_ids = message_link.get_media_link(chat_id, location_id)

#         await self.bot.delete_messages(
#             chat_id, message_ids + [message.message_id]
#         )

#     async def async_start(self) -> None:
#         aiogram_system = AiogramSystem()

#         dp = aiogram_system.dispatcher
#         dp.callback_query.register(self.on_hide, F.data.startswith("hide"))
        
#         self.bot = aiogram_system.bots["karnaukhivka_locations_bot"]



# class Bot_RatingSystem(AsyncSystem):
#     async def update_location(self, message: Message, location: FullLocation) -> None:
#         view_location = Bot_ViewLocationsSystem()
#         await view_location.update_location(message, location)

#     async def on_like(self, callback: CallbackQuery) -> None:
#         location_id = int(callback.data[4:])

#         database = DatabaseSystem()
#         location = await database.like(callback.from_user.id, location_id)

#         if location:
#             await self.update_location(callback.message, location)

#     async def on_dislike(self, callback: CallbackQuery) -> None:
#         location_id = int(callback.data[7:])

#         database = DatabaseSystem()
#         location = await database.dislike(callback.from_user.id, location_id)

#         if location:
#             await self.update_location(callback.message, location)

#     async def async_start(self) -> None:
#         aiogram_system = AiogramSystem()

#         dp = aiogram_system.dispatcher
#         dp.callback_query.register(self.on_like, F.data.startswith("like"))
#         dp.callback_query.register(self.on_dislike, F.data.startswith("dislike"))


# class Bot_CommentSystem(AsyncSystem):
#     bot: TelegramBot

#     async def cancel(self, message: Message, state: FSMContext) -> None:
#         await state.clear()

#         database = DatabaseSystem()
#         is_admin = await database.check_admin(message.from_user.id)

#         bot_menu = Bot_MenuSystem()
#         keyboard = bot_menu.get_menu_keyboard(is_admin)

#         await message.answer(
#             "Скасовано",
#             reply_markup=keyboard
#         )

#     async def on_comment(self, callback: CallbackQuery, state: FSMContext) -> None:
#         location_id = int(callback.data[7:])

#         await state.set_state(CommentForm.comment_text)
#         await state.update_data(
#             location_id=location_id
#         )

#         keyboard = [
#             [ KeyboardButton(text="Скасувати") ]
#         ]

#         await callback.message.answer(
#             "Напишіть Ваше враження про локацію.",
#             reply_markup=ReplyKeyboardMarkup(
#                 keyboard=keyboard, resize_keyboard=True
#             )
#         )

#     async def get_comment_text(self, message: Message, state: FSMContext) -> None:        
#         database = DatabaseSystem()
#         is_admin = await database.check_admin(message.from_user.id)
#         message_id = await database.get_forwarded_message_id(
#             await state.get_value("location_id")
#         )

#         bot_menu = Bot_MenuSystem()
#         menu_keyboard = bot_menu.get_menu_keyboard(is_admin)

#         await state.clear()
#         await message.answer(
#             "Дякуємо за допомогу! Ваш " 
#             "відгук може повпливати на опис.",
#             reply_markup=menu_keyboard
#         )
#         await self.bot.send_message(
#             "@karnaukhivka_locations_chat",
#             f"Анонімний відгук: {message.text}",
#             reply_to_message_id=message_id
#         )

#     async def async_start(self) -> None:
#         aiogram_system = AiogramSystem()

#         dp = aiogram_system.dispatcher
#         dp.message.register(
#             self.cancel, 
#             F.text == "Скасувати", 
#             CommentForm.comment_text
#         )
#         dp.message.register(self.get_comment_text, CommentForm.comment_text)
#         dp.callback_query.register(self.on_comment, F.data.startswith("comment"))

#         self.bot = aiogram_system.bots["karnaukhivka_locations_bot"]


def main() -> None:
    aiogram_system = AiogramSystem()
    aiogram_system.add_bot(
        "karnaukhivka_locations_bot", TOKEN
    )

    AsyncExecutor(
        STORAGE_SYSTEMS + TELEGRAM_SYSTEMS + [
            aiogram_system
        ]
    ).start()


if __name__ == "__main__":
    main()
