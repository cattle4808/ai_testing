from aiogram import Router, types, F
from aiogram.filters import CommandStart

from .. import bot

main = Router()


@main.message(CommandStart())
async def echo(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username
    await message.answer(f'Привет, {username}!')

    await bot.send_message(user_id, 'Привет!')

