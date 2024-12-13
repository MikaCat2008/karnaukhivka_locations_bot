from aiogram.types import (
    KeyboardButton, ReplyKeyboardMarkup
)

from engine.core import System


class Telegram_MarkupsSystem(System):
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

    def get_done_2cancel_markup(self) -> ReplyKeyboardMarkup:
        return ReplyKeyboardMarkup(
            keyboard=[
                [ 
                    KeyboardButton(text="Все"),
                    KeyboardButton(text="Скасувати")
                ],
                [ KeyboardButton(text="Скасувати попередню сторінку") ]
            ],
            resize_keyboard=True
        )
