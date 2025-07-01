from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from bot import dp

admin = Router()

@admin.message(Command("admin_panel"))
async def admin_panel(message: Message):
    await message.answer("Admin panel")