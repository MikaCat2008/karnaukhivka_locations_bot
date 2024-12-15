from typing import Optional
from collections import deque

from aiogram.types import (
    KeyboardButton, ReplyKeyboardMarkup,
    InlineKeyboardButton, InlineKeyboardMarkup
)

from engine.core import System

NUMBERS = [ "0️⃣", "1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣" ]


class Telegram_MarkupsSystem(System):
    def get_menu_markup(self, is_admin: bool) -> ReplyKeyboardMarkup:
        keyboard = [
            [ 
                KeyboardButton(text="Локації"), 
                KeyboardButton(text="Детальніше") 
            ],
            [ 
                KeyboardButton(text="Запропонувати локацію") 
            ]
        ]
        
        if is_admin:
            keyboard.append([ 
                KeyboardButton(text="Перевірити локації") 
            ])

        return ReplyKeyboardMarkup(
            keyboard=keyboard, resize_keyboard=True
        )

    def get_done_markup(self) -> ReplyKeyboardMarkup:
        return ReplyKeyboardMarkup(
            keyboard=[
                [ KeyboardButton(text="Все") ]
            ],
            resize_keyboard=True
        )

    def get_cancel_markup(self) -> ReplyKeyboardMarkup:
        return ReplyKeyboardMarkup(
            keyboard=[
                [ KeyboardButton(text="Скасувати") ]
            ],
            resize_keyboard=True
        )

    def get_done_cancel_markup(self) -> ReplyKeyboardMarkup:
        return ReplyKeyboardMarkup(
            keyboard=[
                [ 
                    KeyboardButton(text="Все"),
                    KeyboardButton(text="Скасувати")
                ]
            ],
            resize_keyboard=True
        )

    def get_locations_markup(
        self, 
        index: int, 
        verified: bool, 
        locations_data: deque[tuple[int, str]]
    ) -> InlineKeyboardMarkup:
        if verified:
            status = ""
        else:
            status = "unverified_"

        inline_keyboard = deque([
            [
                InlineKeyboardButton(
                    text="<",
                    callback_data=f"left_{status}locations"
                ),
                InlineKeyboardButton(
                    text=str(index),
                    callback_data=f" "
                ),
                InlineKeyboardButton(
                    text=">",
                    callback_data=f"right_{status}locations"
                )
            ]
        ])
        
        for id, text in locations_data:
            if verified:
                callback_data = f"location_{id}"
            else:
                callback_data = f"unverified_location_{id}"

            inline_keyboard.append([
                InlineKeyboardButton(
                    text=text, callback_data=callback_data
                )
            ])

        return InlineKeyboardMarkup(
            inline_keyboard=inline_keyboard
        )

    def get_rating_markup(
        self, 
        index: int, 
        likes: int, 
        dislikes: int, 
        message_id: Optional[int],
        rate_value: Optional[bool]
    ) -> InlineKeyboardMarkup:
        if message_id:
            comments = InlineKeyboardButton(
                text=f"Коментарі 🌐",
                url=f"t.me/karnaukhivka_locations_chat/{message_id}"
            )
        else: 
            comments = InlineKeyboardButton(
                text="🚫",
                callback_data=" "
            )

        return InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="◀️",
                    callback_data="left_location"
                ),
                InlineKeyboardButton(
                    text="".join(
                        NUMBERS[int(s)]
                        for s in str(index)
                    ),
                    callback_data=" "
                ),
                InlineKeyboardButton(
                    text="▶️",
                    callback_data="right_location"
                )
            ],
            [
                InlineKeyboardButton(
                    text=f"{'✅    ' if rate_value == 1 else ''}👍 ({likes})",
                    callback_data="like_location"
                ),
                InlineKeyboardButton(
                    text=f"{'✅    ' if rate_value == 0 else ''}👎 ({dislikes})",
                    callback_data="dislike_location"
                )
            ],
            [
                InlineKeyboardButton(
                    text="💬",
                    callback_data="comment_location"
                ),
                comments
            ],
            [
                InlineKeyboardButton(
                    text="Приховати",
                    callback_data="hide_location"
                )
            ]
        ])

    def get_verification_markup(self, index: int) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="◀️",
                        callback_data="left_unverified_location"
                    ),
                    InlineKeyboardButton(
                        text="".join(
                            NUMBERS[int(s)]
                            for s in str(index)
                        ),
                        callback_data=" "
                    ),
                    InlineKeyboardButton(
                        text="▶️",
                        callback_data="right_unverified_location"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="✅",
                        callback_data="verify_location"
                    ),
                    InlineKeyboardButton(
                        text="❌",
                        callback_data="deny_location"
                    )
                ]
            ]
        )
