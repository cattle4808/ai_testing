import asyncio

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

from bot import CommandMap

admin = Router()

@admin.message(Command("admin_panel"))
async def admin_panel(message: Message):
    await message.answer("Admin panel")

@admin.message(F.text == CommandMap.Admin.DEV_MENU)
async def dev_panel(message: Message):
    await message.answer("Dev panel")



