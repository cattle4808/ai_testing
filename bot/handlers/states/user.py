from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from asgiref.sync import sync_to_async
import json

from ... fsm.user import UserPaymentCheck
from ... fsm.admin import AdminPaymentCheck
from ... import bot, redis
from .. user import admin_inline, user_inline
from services.models import operations

state_user = Router()


@state_user.message(UserPaymentCheck.waiting_for_img, F.photo)
async def get_payment_img(message: types.Message, state: FSMContext):
    await message.delete()
    redis_data = await state.get_data()
    redis_key = redis_data.get("redis_key")

    if not redis_key:
        await state.clear()
        return

    raw_data = await redis.get(f"buy_script:{redis_key}")
    if not raw_data:
        return
    data = json.loads(raw_data)

    payment_msg_id = data.get("payment_msg_id")

    await bot.edit_message_reply_markup(
        chat_id=message.from_user.id,
        message_id=payment_msg_id,
        reply_markup=None,
        # parse_mode = "HTML"
    )

    photo = message.photo[-1]
    file_id = photo.file_id



    await state.set_state(UserPaymentCheck.waiting_for_accept)

    data["file_id"] = file_id
    await redis.set(f"buy_script:{redis_key}", json.dumps(data))

    await state.set_state(UserPaymentCheck.waiting_for_accept)

    caption = (f"🆔: <code>{data.get('key')}</code>\n\n"
               f"start_at: <code>{data.get('start_at')}</code>\n"
               f"stop_at: <code>{data.get('stop_at')}</code>\n\n"
               f"payment_sum: <code>{data.get('payment_sum')}</code>\n\n")

    msg =await bot.send_photo(
        chat_id=message.from_user.id,
        photo=file_id,
        caption=caption,
        reply_markup=user_inline.send_or_receive_payment(redis_key),
        parse_mode="HTML"
    )

    data["send_payment_msg_id"] = msg.message_id
    await redis.set(f"buy_script:{redis_key}", json.dumps(data))



@state_user.message(UserPaymentCheck.waiting_for_img)
async def handle_not_photo(message: types.Message):
    await message.answer("❌ Это не фото. Пожалуйста, пришли именно изображение.")



