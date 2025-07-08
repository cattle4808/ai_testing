from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from asgiref.sync import sync_to_async

from ... fsm.user import UserPaymentCheck
from ... import bot
from .. user import admin_inline
from services.models import operations

state_user = Router()


@state_user.message(UserPaymentCheck.waiting_for_img, F.photo)
async def get_payment_img(message: types.Message, state: FSMContext):
    data = await state.get_data()
    redis_key = data.get("redis_key")

    if not redis_key:
        await message.answer("⚠️ Ошибка: не найден redis_key. Попробуй заново.")
        await state.clear()
        return

    photo = message.photo[-1]
    file_id = photo.file_id

    admins = await sync_to_async(operations.get_admins)()

    for admin in admins:
        print("send_photo_to_admin:", admin)
        await bot.send_photo(
            chat_id=admin.get('user'),
            photo=file_id,
            caption=f'User: {message.from_user.id}\n',
            reply_markup=admin_inline.check_payment(redis_key)
        )

    await message.answer("идет проверка")
    await state.clear()



@state_user.message(UserPaymentCheck.waiting_for_img)
async def handle_not_photo(message: types.Message):
    await message.answer("❌ Это не фото. Пожалуйста, пришли именно изображение.")



