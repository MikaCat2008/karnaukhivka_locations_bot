from typing import Optional
from collections import deque
from dataclasses import dataclass

from aiogram import F, Bot as TelegramBot
from aiogram.types import (
    Message, CallbackQuery,
    InputMedia, InputMediaPhoto, InputMediaVideo,
    KeyboardButton, ReplyKeyboardMarkup,
    InlineKeyboardButton, InlineKeyboardMarkup
)
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiosqlite import Connection, connect

from core import (
    AsyncSystem, AiogramSystem, AsyncExecutor
)
from config import TOKEN


@dataclass
class ShortLocation:
    id: int
    name: str
    rating: float


@dataclass
class FullLocation:
    id: int
    name: str
    info: str
    media: list[str]
    likes: int
    rating: float
    dislikes: int


class OfferLocationForm(StatesGroup):
    location_name = State()
    location_info = State()
    location_media = State()


class DatabaseSystem(AsyncSystem):
    connection: Connection

    def __init__(self) -> None:
        super().__init__()

        self.connection = connect("database.db", isolation_level=None)

    def calc_rating(self, likes: int, dislikes: int) -> float:
        if likes + dislikes == 0:
            return 5
        
        return round(5 * likes / (likes + dislikes), 1)
            
    async def create_tables(self) -> None:
        await self.connection.executescript(
            """
                CREATE TABLE IF NOT EXISTS media (
                    location_id INTEGER,
                    file_id STRING
                );
                CREATE TABLE IF NOT EXISTS ratings (
                    location_id INTEGER,
                    status BOOLEAN,
                    user_id INTEGER
                );
                CREATE TABLE IF NOT EXISTS locations (
                    id INTEGER PRIMARY KEY,
                    name STRING,
                    info STRING,
                    likes INTEGER,
                    dislikes INTEGER
                )
            """
        )

    async def get_rating(self, user_id: int, location_id: int) -> object:
        async with await self.connection.execute(
            "SELECT * FROM ratings WHERE user_id=? AND location_id=?",
            ( user_id, location_id )
        ) as cursor:
            return await cursor.fetchone()

    async def like(self, user_id: int, location_id: int) -> Optional[FullLocation]:        
        if await self.get_rating(user_id, location_id):
            return
        
        await self.connection.execute(
            "UPDATE locations SET likes=likes + 1 WHERE id=?",
            ( location_id, )
        )
        await self.connection.execute(
            "INSERT INTO ratings(location_id, status, user_id) "
            "VALUES(?, TRUE, ?)",
            ( location_id, user_id )
        )
        
        return await self.get_location(location_id)

    async def dislike(self, user_id: int, location_id: int) -> Optional[FullLocation]:
        if await self.get_rating(user_id, location_id):
            return
            
        await self.connection.execute(
            "UPDATE locations SET dislikes=dislikes + 1 WHERE id=?",
            ( location_id, )
        )
        await self.connection.execute(
            "INSERT INTO ratings(location_id, status, user_id) "
            "VALUES(?, FALSE, ?)",
            ( location_id, user_id )
        )

        return await self.get_location(location_id)

    async def create_location(self, name: str, info: str, media: list[str]) -> FullLocation:
        async with await self.connection.execute(
            "INSERT INTO locations(id, name, info, likes, dislikes) "
            f"VALUES(NULL, ?, ?, ?, ?)",
            ( name, info, 0, 0 )
        ) as cursor:
            location_id = cursor.lastrowid

        await self.connection.execute(
            "INSERT INTO media(location_id, file_id) "
            f"VALUES {', '.join([f'({location_id}, ?)'] * len(media))}",
            media
        )

        return FullLocation(
            id=location_id,
            name=name,
            info=info,
            likes=0,
            media=media,
            rating=5,
            dislikes=0
        )

    async def get_location(self, location_id: int) -> FullLocation:
        async with await self.connection.execute(
            "SELECT file_id FROM media WHERE location_id=?",
            ( location_id, )
        ) as cursor:
            rows = await cursor.fetchall()
            media = list(map(lambda f: f[0], rows))

        async with await self.connection.execute(
            "SELECT * FROM locations WHERE id=?",
            ( location_id, )
        ) as cursor:
            location_id, name, info, likes, dislikes = await cursor.fetchone()

        return FullLocation(
            id=location_id,
            name=name,
            info=info,
            media=media,
            likes=likes,
            rating=self.calc_rating(likes, dislikes),
            dislikes=dislikes
        )
        
    async def get_short_locations(self) -> list[ShortLocation]:
        async with self.connection.execute(
            "SELECT id, name, likes, dislikes FROM locations"
        ) as cursor:
            rows = await cursor.fetchall()
            
            return [
                ShortLocation(
                    id=id,
                    name=name,
                    rating=self.calc_rating(likes, dislikes)
                )
                for id, name, likes, dislikes in rows
            ]

    async def async_start(self) -> None:
        await self.connection
        await self.create_tables()

        return

        await self.create_location(
            "Ліцей №38", 
            "Знаходиться на вулиці Батальйону ім. Шейха "
            "Мансура 17А",
            [
                "photo_AgACAgIAAxkBAAIBGWdV22lr9VGpRX9MHapIMjFaI9XDAAJhDDIbcyGxSmAi-gcEjuzeAQADAgADcwADNgQ"
            ]
        )
        await self.create_location(
            "Чимбар", 
            "Знаходиться на вулиці Батальйону ім. Шейха "
            "Мансура, 14Б",
            [
                "photo_AgACAgIAAxkBAAIBJGdV3K7zVcnAmAS57Akim8nABdiZAAKADDIbcyGxSo7JLobXm8ArAQADAgADcwADNgQ"
            ]
        )
        await self.create_location(
            "Дитячий садок", 
            "Знаходиться на вулиці Батальйону ім. Шейха "
            "Манусра, 30Г",
            [
                "photo_AgACAgIAAxkBAAIBJWdV3O8mpxpW2U6PkS0ZNOcH-Iy6AAKBDDIbcyGxStmHtkew8QbIAQADAgADcwADNgQ"
            ]
        )


class Bot_MenuSystem(AsyncSystem):
    def get_menu_keyboard(self) -> InlineKeyboardMarkup:
        return ReplyKeyboardMarkup(
            keyboard=[
                [ 
                    KeyboardButton(text="Локації"), 
                    KeyboardButton(text="Детальніше") 
                ],
                [ 
                    KeyboardButton(text="Запропонувати локацію") 
                ]
            ], 
            resize_keyboard=True
        )

    async def on_start(self, message: Message) -> None:
        await message.answer(
            "Я - бот, створений для допомоги жителям селища Карнаухівка. "
            "Для подробиць тисніть кнопку \"Детальніше\".",
            reply_markup=self.get_menu_keyboard()
        )

    async def on_details(self, message: Message) -> None:
        await message.answer(
            "Сенс боту - надати мешканцям селища можливість дізнатись "
            "нового про своє селище. Він дасть відповідь на питання: "
            "\"А де можна сьогодні погуляти?\", запропонувавши цікаві "
            "та популярні локації, в залежності від Ваших потреб. "
            "Більшість локацій має фото або відео, тому Ви можете "
            "одразу побачити, що Вас там буде чекає. Але якщо фото чи "
            "відео немає, ви все одно зможете дізнатись багато "
            "інформації про локацію, бо до кожної з них йде детальний "
            "опис, історичні факти та рейтинг, завдяки якому Ви "
            "можете швидко дізнатись актуальність локації.\n\n"

            "Також Ви можете допомогти боту, запропонувавши свою "
            "локацію. Вона перевіриться модераторами і буде додана "
            "до списку."
        )

    async def async_start(self) -> None:
        aiogram_system = AiogramSystem()

        dp = aiogram_system.dispatcher
        dp.message.register(self.on_start, F.text == "/start")
        dp.message.register(self.on_details, F.text == "Детальніше")


class Bot_ViewLocationsSystem(AsyncSystem):
    bot: TelegramBot
    media_message_ids: dict[int, dict[int, list[int]]]
    
    def __init__(self) -> None:
        super().__init__()

        self.media_message_ids = {}

    def get_location_short_text(self, location: ShortLocation) -> str:
        return "{} | {}".format(location.rating, location.name)
    
    def get_location_full_text(self, location: FullLocation) -> str:
        return (
            "Назва: {}\n"
            "Рейтинг: {} / 5\n\n"
            "{}"
        ).format(location.name, location.rating, location.info)
    
    def get_location_inline_keyboard(self, location: FullLocation) -> None:
        return InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f"({location.likes}) Подобається",
                    callback_data=f"like{location.id}"
                ),
                InlineKeyboardButton(
                    text=f"({location.dislikes}) Не подобається",
                    callback_data=f"dislike{location.id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="Коментувати",
                    callback_data=f"comment{location.id}"
                ),
                InlineKeyboardButton(
                    text=f"Переглянути коментарі",
                    callback_data=f"view_comments{location.id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="Приховати",
                    callback_data=f"hide{location.id}"
                )
            ]
        ])

    async def get_locations(self, message: Message) -> None:
        start_index = 1
        finish_index = 3

        database = DatabaseSystem()
        short_locations = await database.get_short_locations()
        
        inline_keyboard = [
            [
                InlineKeyboardButton(
                    text=self.get_location_short_text(location),
                    callback_data=f"loc{location.id}"
                )
            ]
            for location in short_locations
        ]
        
        await message.answer(
            f"Локації ({start_index} - {finish_index})",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=inline_keyboard
            )
        )

    async def on_loc(self, callback: CallbackQuery) -> None:
        location_id = int(callback.data[3:])
        
        database = DatabaseSystem()
        location = await database.get_location(location_id)

        await self.send_location(callback.message, location)

    async def on_hide(self, callback: CallbackQuery) -> None:
        message = callback.message
        location_id = int(callback.data[4:])

        chat_id = message.chat.id
        message_ids = self.media_message_ids[location_id][chat_id]

        await self.bot.delete_messages(
            chat_id, message_ids + [message.message_id]
        )

    async def send_media(self, chat_id: int, media: deque[str]) -> list[Message]:
        media_data: deque[InputMedia] = deque()

        for file_id in media:
            content_type = file_id[:5]
            file_id = file_id[6:]
            
            if content_type == "photo":
                media_data.append(InputMediaPhoto(media=file_id))
            else:
                media_data.append(InputMediaVideo(media=file_id))

        return await self.bot.send_media_group(chat_id, list(media_data))

    async def send_location(self, message: Message, location: FullLocation) -> None:
        if location.media:
            media_messages = await self.send_media(message.chat.id, location.media)

            if location.id not in self.media_message_ids:
                self.media_message_ids[location.id] = {}

            self.media_message_ids[location.id][message.chat.id] = [
                message.message_id for message in media_messages
            ]

        await message.answer(
            text=self.get_location_full_text(location),
            reply_markup=self.get_location_inline_keyboard(location)
        )

    async def send_new_location(self, location: FullLocation) -> None:
        await self.send_media("@karnaukhivka_locations", location.media)
        await self.bot.send_message("@karnaukhivka_locations", f"Нова локація: {location.name}")

    async def update_location(self, message: Message, location: FullLocation) -> None:
        await message.edit_text(
            text=self.get_location_full_text(location),
            reply_markup=self.get_location_inline_keyboard(location)
        )

    async def async_start(self) -> None:
        aiogram_system = AiogramSystem()

        dp = aiogram_system.dispatcher
        dp.message.register(self.get_locations, F.text == "Локації")
        dp.callback_query.register(self.on_loc, F.data.startswith("loc"))
        dp.callback_query.register(self.on_hide, F.data.startswith("hide"))

        self.bot = aiogram_system.bots["karnaukhivka_locations_bot"]


class Bot_RatingSystem(AsyncSystem):
    async def update_location(self, message: Message, location: FullLocation) -> None:
        view_location = Bot_ViewLocationsSystem()
        await view_location.update_location(message, location)

    async def on_like(self, callback: CallbackQuery) -> None:
        location_id = int(callback.data[4:])

        database = DatabaseSystem()
        location = await database.like(callback.from_user.id, location_id)

        if location:
            await self.update_location(callback.message, location)

    async def on_dislike(self, callback: CallbackQuery) -> None:
        location_id = int(callback.data[7:])

        database = DatabaseSystem()
        location = await database.dislike(callback.from_user.id, location_id)

        if location:
            await self.update_location(callback.message, location)

    async def async_start(self) -> None:
        aiogram_system = AiogramSystem()

        dp = aiogram_system.dispatcher
        dp.callback_query.register(self.on_like, F.data.startswith("like"))
        dp.callback_query.register(self.on_dislike, F.data.startswith("dislike"))


class Bot_CommentSystem(AsyncSystem):
    ...


class Bot_OfferLocationSystem(AsyncSystem):
    async def offer_location(self, message: Message, state: FSMContext) -> None:
        await state.set_state(OfferLocationForm.location_name)
        await message.answer(
            "Спочатку напишіть коротку назву локації."
        )

    async def set_location_name(self, message: Message, state: FSMContext) -> None:
        await state.update_data(
            location_name=message.text
        )
        await state.set_state(OfferLocationForm.location_info)
        await message.answer(
            "Тепер напишіть опис локації: як туди дібратись, "
            "чим ця локація цікава та що там можна зробити."
        )

    async def set_location_info(self, message: Message, state: FSMContext) -> None:
        await state.update_data(
            location_info=message.text,
            location_media_count=0
        )
        await state.set_state(OfferLocationForm.location_media)

        keyboard = [
            [ KeyboardButton(text="Все") ]
        ]

        await message.answer(
            "Наостанок можете надіслати декілька фото чи відео."
            "Коли завершите, натисніть кнопку \"Все\"",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=keyboard, resize_keyboard=True
            )
        )

    async def add_location_media(self, message: Message, state: FSMContext) -> None:
        media_count: int = await state.get_value("location_media_count")
        content_type: str = message.content_type

        if content_type == "photo":
            file_id = "photo_" + message.photo[0].file_id
        else:
            file_id = "video_" + message.video.file_id

        await state.update_data({
            "location_media_count": media_count + 1,
            f"location_file_id_{media_count}": file_id 
        })

    async def set_location_media(self, message: Message, state: FSMContext) -> None:
        data = await state.get_data()

        bot_menu_system = Bot_MenuSystem()
        menu_keyboard = bot_menu_system.get_menu_keyboard()

        await state.clear()
        await message.answer(
            "Дякуємо за внесок у нашого з Вами боту, цим Ви "
            "робите наше селище краще! Локація у найближчий "
            "час буде перевірена модераторами.",
            reply_markup=menu_keyboard
        )

        location_name: str = data["location_name"]
        location_info: str = data["location_info"]
        location_media: deque[str] = deque()
        location_media_count = data["location_media_count"]

        for i in range(location_media_count):
            location_media.append(
                data[f"location_file_id_{i}"]
            )

        database = DatabaseSystem()
        location = await database.create_location(
            location_name, location_info, location_media
        )

        view_location = Bot_ViewLocationsSystem()
        await view_location.send_location(message, location)
        await view_location.send_new_location(location)

    async def async_start(self) -> None:
        aiogram_system = AiogramSystem()

        dp = aiogram_system.dispatcher
        dp.message.register(self.offer_location, F.text == "Запропонувати локацію")
        dp.message.register(self.set_location_name, OfferLocationForm.location_name)
        dp.message.register(self.set_location_info, OfferLocationForm.location_info)
        dp.message.register(
            self.add_location_media, 
            F.photo | F.video,
            OfferLocationForm.location_media
        )
        dp.message.register(
            self.set_location_media, 
            F.text == "Все", 
            OfferLocationForm.location_media
        )


def main() -> None:
    aiogram_system = AiogramSystem()
    aiogram_system.add_bot(
        "karnaukhivka_locations_bot", TOKEN
    )
    database_system = DatabaseSystem()
    
    AsyncExecutor([
        database_system,
        aiogram_system,
        Bot_MenuSystem(),
        Bot_RatingSystem(),
        Bot_CommentSystem(),
        Bot_ViewLocationsSystem(),
        Bot_OfferLocationSystem()
    ]).start()


if __name__ == "__main__":
    main()
