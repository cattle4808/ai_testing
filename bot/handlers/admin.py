import asyncio

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

from bot import dp

admin = Router()

@admin.message(Command("admin_panel"))
async def admin_panel(message: Message):
    await message.answer("Admin panel")

@admin.message(F.text == "Dev_panel")
async def dev_panel(message: Message):
    await message.answer("Dev panel")
    await asyncio.sleep(1)
    await message.reply("Dev panel.")
    await asyncio.sleep(1)
    await message.reply("Dev panel..")
    await asyncio.sleep(1)
    await message.reply("Dev panel...")
    await asyncio.sleep(1)
    await message.reply("Dev panel....")
    await asyncio.sleep(1)
    await message.reply("Dev panel.....")
    await asyncio.sleep(1)
    await message.reply("Dev panel......")
    await asyncio.sleep(1)
    await message.reply("Dev panel.......")
