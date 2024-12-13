from engine.async_executor import AsyncExecutor
from engine.aiogram_system import AiogramSystem

from storage_systems import SYSTEMS as STORAGE_SYSTEMS
from telegram_systems import SYSTEMS as TELEGRAM_SYSTEMS

from config import TOKEN

# NUMBERS = [ "0️⃣", "1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣" ]


# class Bot_ViewLocationSystem(AsyncSystem):
#     bot: TelegramBot

#     async def send_media(self, chat_id: int, media: deque[str]) -> list[Message]:
#         media_data: deque[InputMedia] = deque()

#         for file_id in media:
#             content_type = file_id[:5]
#             file_id = file_id[6:]
            
#             if content_type == "photo":
#                 media_data.append(InputMediaPhoto(media=file_id))
#             else:
#                 media_data.append(InputMediaVideo(media=file_id))

#         return await self.bot.send_media_group(chat_id, list(media_data))

#     async def send_location(self, message: Message, location: FullLocation) -> None:
#         if location.media:
#             media_messages = await self.send_media(message.chat.id, location.media)

#             media = [
#                 message.message_id for message in media_messages
#             ]

#             message_link = MessageLinkSystem()
#             message_link.add_media_link(media, message.chat.id, location.id)

#         database = DatabaseSystem()
#         message_id = await database.get_forwarded_message_id(location.id)

#         pages = Bot_PagesSystem()
#         pages.set_page(0, message.chat.id, location.id)

#         await message.answer(
#             text=self.get_location_full_text(location, 0),
#             reply_markup=self.get_location_inline_keyboard(
#                 location, message_id, 0
#             )
#         )

#     async def send_new_location(self, location: FullLocation) -> None:
#         if location.media:
#             await self.send_media("@karnaukhivka_locations", location.media)

#         message = await self.bot.send_message(
#             "@karnaukhivka_locations", 
#             f"Нова локація: {location.name}"
#         )

#         message_link = MessageLinkSystem()
#         message_link.add_location_link(message.message_id, location.id)
    
#     async def update_location(self, message: Message, location: FullLocation) -> None:
#         database = DatabaseSystem()
#         message_id = await database.get_forwarded_message_id(location.id)

#         pages = Bot_PagesSystem()
#         current_page = pages.get_current(message.chat.id, location.id)

#         await message.edit_text(
#             text=self.get_location_full_text(location, current_page),
#             reply_markup=self.get_location_inline_keyboard(
#                 location, message_id, current_page
#             )
#         )
    
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


# class Bot_PagesSystem(AsyncSystem):
#     pages: dict[int, dict[int, int]]

#     def __init__(self) -> None:
#         self.pages = {}

#     def set_page(self, page: int, user_id: int, location_id: int) -> None:
#         if location_id not in self.pages:
#             self.pages[location_id] = {}

#         self.pages[location_id][user_id] = page

#     def get_current(self, user_id: int, location_id: int) -> int:
#         return self.pages[location_id][user_id]

#     async def on_left(self, callback: CallbackQuery) -> None:
#         message = callback.message
#         chat_id = message.chat.id
#         location_id = int(callback.data[4:])

#         if self.pages[location_id][chat_id] == 0:
#             return

#         self.pages[location_id][chat_id] -= 1

#         view_location = Bot_ViewLocationSystem()
#         await view_location.update_location_by_id(message, location_id)

#     async def on_right(self, callback: CallbackQuery) -> None:
#         message = callback.message
#         chat_id = message.chat.id
#         location_id = int(callback.data[5:])

#         self.pages[location_id][chat_id] += 1

#         view_location = Bot_ViewLocationSystem()
#         await view_location.update_location_by_id(message, location_id)

#     async def async_start(self) -> None:
#         aiogram_system = AiogramSystem()

#         dp = aiogram_system.dispatcher
#         dp.callback_query.register(self.on_left, F.data.startswith("left"))
#         dp.callback_query.register(self.on_right, F.data.startswith("right"))


# class Bot_ViewLocationsSystem(AsyncSystem):
#     bot: TelegramBot

#     def get_location_short_text(self, location: ShortLocation) -> str:
#         return "{} | {}".format(location.rating, location.name)
    
#     def get_location_full_text(self, location: FullLocation, current_page: int) -> str:
#         info = location.info[current_page * 1000:(current_page + 1) * 1000]

#         if len(location.info) > (current_page + 1) * 1000:
#             info += "..."
        
#         return (
#             "Назва: {}\n"
#             "Рейтинг: {} / 5\n\n"
#             "{}"
#         ).format(location.name, location.rating, info)
    
#     def get_location_inline_keyboard(
#         self, 
#         location: FullLocation, 
#         message_id: Optional[int],
#         current_page: int
#     ) -> None:
#         return InlineKeyboardMarkup(inline_keyboard=[
#             [
#                 InlineKeyboardButton(
#                     text=f"◀️",
#                     callback_data=f"left{location.id}"
#                 ),
#                 InlineKeyboardButton(
#                     text="".join(
#                         NUMBERS[int(s)]
#                         for s in str(current_page + 1)
#                     ),
#                     callback_data=" "
#                 ),
#                 InlineKeyboardButton(
#                     text=f"▶️",
#                     callback_data=f"right{location.id}"
#                 )
#             ],
#             [
#                 InlineKeyboardButton(
#                     text=f"({location.likes}) 👍",
#                     callback_data=f"like{location.id}"
#                 ),
#                 InlineKeyboardButton(
#                     text=f"({location.dislikes}) 👎",
#                     callback_data=f"dislike{location.id}"
#                 )
#             ],
#             [
#                 InlineKeyboardButton(
#                     text="💬",
#                     callback_data=f"comment{location.id}"
#                 ),
#                 (
#                     InlineKeyboardButton(
#                         text=f"Коментарі 🌐",
#                         url=f"t.me/karnaukhivka_locations_chat/{message_id}"
#                     )
#                     if message_id
#                     else 
#                     InlineKeyboardButton(
#                         text="🚫",
#                         callback_data=" "
#                     )
#                 )
#             ],
#             [
#                 InlineKeyboardButton(
#                     text="Приховати",
#                     callback_data=f"hide{location.id}"
#                 )
#             ]
#         ])

#     async def get_locations(self, message: Message) -> None:
#         database = DatabaseSystem()
#         short_locations = await database.get_short_locations()
        
#         inline_keyboard = [
#             [
#                 InlineKeyboardButton(
#                     text=self.get_location_short_text(location),
#                     callback_data=f"loc{location.id}"
#                 )
#             ]
#             for location in short_locations
#         ]
        
#         await message.answer(
#             f"Локації (1 - {len(short_locations)})",
#             reply_markup=InlineKeyboardMarkup(
#                 inline_keyboard=inline_keyboard
#             )
#         )

#     async def on_loc(self, callback: CallbackQuery) -> None:
#         location_id = int(callback.data[3:])
        
#         database = DatabaseSystem()
#         location = await database.get_location(location_id)

#         await self.send_location(callback.message, location)

#     async def async_start(self) -> None:
#         aiogram_system = AiogramSystem()

#         dp = aiogram_system.dispatcher
#         dp.message.register(self.get_locations, F.text == "Локації")
#         dp.callback_query.register(self.on_loc, F.data.startswith("loc"))

#         self.bot = aiogram_system.bots["karnaukhivka_locations_bot"]


# class Bot_ForwardSystem(AsyncSystem):
#     async def forwarded(self, message: Message) -> None:
#         message_id = message.forward_from_message_id
#         message_link = MessageLinkSystem()

#         if message_id not in message_link.location_links:
#             return await message.delete()
        
#         location_id = message_link.get_location_link(message_id)
#         message_link.remove_location_link(message_id)
        
#         database = DatabaseSystem()
#         await database.add_forwarded_message_id(location_id, message.message_id)
    
#     async def async_start(self) -> None:
#         aiogram_system = AiogramSystem()

#         dp = aiogram_system.dispatcher
#         dp.message.register(self.forwarded, F.from_user.id == 777000)


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


# class Bot_AdminSystem(AsyncSystem):
#     async def admin_filter(self, message: Message) -> bool:
#         database = DatabaseSystem()
        
#         return await database.check_admin(message.from_user.id)


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
