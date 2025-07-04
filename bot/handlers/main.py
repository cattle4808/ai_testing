from aiogram import Router, types, F
from aiogram.filters import CommandStart
from asgiref.sync import sync_to_async

from .. import bot
from services.models import operations

main = Router()


@main.message(CommandStart())
async def echo(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username
    await message.answer(f'Привет, {username}!')
    await bot.send_message(user_id, 'Привет!')

    await sync_to_async(operations.get_or_create_tg_user)(user_id)

    if await sync_to_async(operations.is_admin)(user_id):
        await bot.send_message(user_id, 'Вы администратор')
        return

    await bot.send_message(user_id, 'Вы не администратор')



