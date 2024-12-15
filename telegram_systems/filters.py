from aiogram.types import Message

from storage_systems import Storage_AdminSystem


async def admin_filter(message: Message) -> bool:
    storage_admin = Storage_AdminSystem()
    
    return await storage_admin.check_admin_session(message.chat.id)
