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
    try:
        await message.delete()
    except:
        pass

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

    try:
        await bot.edit_message_reply_markup(
            chat_id=message.from_user.id,
            message_id=payment_msg_id,
            reply_markup=None
        )
    except:
        pass

    photo = message.photo[-1]
    file_id = photo.file_id

    await state.set_state(UserPaymentCheck.waiting_for_accept)

    data["file_id"] = file_id
    await redis.set(f"buy_script:{redis_key}", json.dumps(data))

    await state.set_state(UserPaymentCheck.waiting_for_accept)

    caption = (
        f"🆔 <code>{data.get('key')}</code>\n"
        f"⏱ <b>Начало:</b> <code>{data.get('start_at')}</code>\n"
        f"⏳ <b>Конец:</b> <code>{data.get('stop_at')}</code>\n\n"
        f"💰 <b>Сумма:</b> <code>{data.get('payment_sum')}</code> сум"
    )

    msg =await bot.send_photo(
        chat_id=message.from_user.id,
        photo=file_id,
        caption=caption,
        reply_markup=user_inline.send_or_receive_payment(redis_key),
        parse_mode="HTML"
    )

    data["send_payment_msg_id"] = msg.message_id
    await redis.set(f"buy_script:{redis_key}", json.dumps(data))

# @state_user.message(UserPaymentCheck.waiting_for_img, F.photo)
# async def get_payment_img(message: types.Message, state: FSMContext):
#     try:
#         await message.delete()
#     except:
#         pass
#
#     redis_data = await state.get_data()
#     redis_key = redis_data.get("redis_key")
#
#     if not redis_key:
#         await state.clear()
#         return
#
#     raw_data = await redis.get(f"buy_script:{redis_key}")
#     if not raw_data:
#         return
#
#     data = json.loads(raw_data)
#
#     payment_msg_id = data.get("payment_msg_id")
#     if payment_msg_id:
#         try:
#             await bot.edit_message_reply_markup(
#                 chat_id=message.from_user.id,
#                 message_id=payment_msg_id,
#                 reply_markup=None
#             )
#         except:
#             pass
#
#     old_msg_id = data.get("send_payment_msg_id")
#     if old_msg_id:
#         try:
#             await bot.delete_message(
#                 chat_id=message.from_user.id,
#                 message_id=old_msg_id
#             )
#         except:
#             pass
#
#     file_id = message.photo[-1].file_id
#
#     data["file_id"] = file_id
#     await redis.set(f"buy_script:{redis_key}", json.dumps(data))
#
#     await state.set_state(UserPaymentCheck.waiting_for_accept)
#
#     caption = (
#         f"🆔 <b>Ключ:</b> <code>{data.get('key')}</code>\n"
#         f"⏱ <b>Начало:</b> <code>{data.get('start_at')}</code>\n"
#         f"⏳ <b>Конец:</b> <code>{data.get('stop_at')}</code>\n\n"
#         f"💰 <b>Сумма:</b> <code>{data.get('payment_sum')}</code> сум"
#     )
#
#     msg = await bot.send_photo(
#         chat_id=message.from_user.id,
#         photo=file_id,
#         caption=caption,
#         reply_markup=user_inline.send_or_receive_payment(redis_key),
#         parse_mode="HTML"
#     )
#
#     data["send_payment_msg_id"] = msg.message_id
#     await redis.set(f"buy_script:{redis_key}", json.dumps(data))




@state_user.message(UserPaymentCheck.waiting_for_img)
async def handle_not_photo(message: types.Message, state: FSMContext):
    try:
        await message.delete()
    except:
        pass

    redis_data = await state.get_data()
    redis_key = redis_data.get("redis_key")

    await message.answer(
        "❌ <b>Нужно отправить именно фото</b>\n\n"
        "Пожалуйста, прикрепи <u>скриншот или фото чека</u> как изображение.\n\n"
        "Или же можете отменить покупку.",
        parse_mode="HTML",
        reply_markup=user_inline.cancel_keyboard(redis_key=redis_key) if redis_key else None
    )
