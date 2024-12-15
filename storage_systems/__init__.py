from .database import DatabaseSystem

from .admin import Storage_AdminSystem
from .pages import Storage_PagesSystem
from .rating import Storage_RatingSystem
from .location import Storage_LocationSystem
from .telegram import Storage_TelegramSystem as Storage_TelegramSystem

SYSTEMS = [
    DatabaseSystem(),
    
    Storage_AdminSystem(),
    Storage_PagesSystem(),
    Storage_RatingSystem(),
    Storage_LocationSystem(),
    Storage_TelegramSystem()
]
