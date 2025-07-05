from aiogram import Router
from aiogram import F, types

from bot.keyboards.user import inline as user_inline, reply as user_reply
from bot.keyboards.admin import inline as admin_inline, reply as admin_reply

user = Router()

@user.message(F.text == "Купить скрипт")
async def buy_script(message: types.Message):
    ...

@user.message(F.text == "Мои скрипты")
async def buy_script(message: types.Message):
    ...

@user.message(F.text == "Инструкция")
async def buy_script(message: types.Message):
    ...

@user.message(F.text == "Поддержка")
async def buy_script(message: types.Message):
    ...