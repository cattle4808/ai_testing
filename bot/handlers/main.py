from aiogram import Router, types, F
from aiogram.filters import CommandStart


main = Router()

@main.message(CommandStart())
async def echo(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username
    await message.answer(f'Привет, {username}!')
