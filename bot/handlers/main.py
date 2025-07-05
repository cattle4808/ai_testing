from aiogram import Router, types, F
from aiogram.filters import CommandStart
from asgiref.sync import sync_to_async

from .. import bot
from services.models import operations

from ..keyboards.user import inline as user_inline, reply as user_reply
from ..keyboards.admin import inline as admin_inline, reply as admin_reply


main = Router()


@main.message(CommandStart())
async def echo(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username or "ГОСТЬ"

    user = await sync_to_async(operations.get_or_create_tg_user)(user_id)

    await message.answer(
        str(user)
    )
    if await sync_to_async(operations.is_admin)(user_id):
        await bot.send_message(user_id, 'Вы администратор')
        await message.answer('Привет, администратор!', reply_markup=admin_reply.main_menu())
        return

    await message.answer(f'Привет, {username}!', reply_markup=user_reply.main_menu())




