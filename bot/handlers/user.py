from aiogram import Router
from aiogram import F, types

from bot.keyboards.user import inline as user_inline, reply as user_reply
from bot.keyboards.admin import inline as admin_inline, reply as admin_reply
from bot import CommandMap

user = Router()

@user.message(F.text == CommandMap.User.BUY_SCRIPT)
async def buy_script(message: types.Message):
    await message.answer("Выберите скрипт")

@user.message(F.text == CommandMap.User.MY_SCRIPTS)
async def my_scripts(message: types.Message):
    await message.answer("Мои скрипты")

@user.message(F.text == CommandMap.User.INSTRUCTION)
async def instruction(message: types.Message):
    await message.answer("Инструкция")

@user.message(F.text == CommandMap.User.SUPPORT)
async def support(message: types.Message):
    await message.answer("Поддержка")

@user.message(F.text == CommandMap.User.MY_DATA)
async def my_data(message: types.Message):
    await message.answer("Мои данные")


