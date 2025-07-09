import json
from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from asgiref.sync import sync_to_async

from services.models import operations
from ... import redis, bot

admin_callback = Router()


@admin_callback.callback_query(F.data.regexp(r"allow_payment_from_admin:(.+)$"))
async def allow_payment_from_admin_handler(callback: types.CallbackQuery, state: FSMContext):
    redis_key = callback.data.split("allow_payment_from_admin:")[1]
    raw_data = json.loads(await redis.get(f"buy_script:{redis_key}"))

    key = raw_data.get("key")

    change_script = await sync_to_async(operations.change_script_status)(key, True)
    # await bot.delete_message(
    #     chat_id=raw_data.get("user_id"),
    #     message_id=raw_data.get("payment_msg_id")
    # )

    await bot.send_message(
        chat_id=raw_data.get("user_id"),
        text=f"Оплата принятат\n\n"
             f"{change_script}"

    )

    for admin in raw_data.get("admins"):
        await bot.edit_message_caption(
            chat_id=int(admin),
            message_id=raw_data.get("payment_msg_id"),
            caption=f" {raw_data}: \n\nОплата принята",
            reply_markup=None
        )

@admin_callback.callback_query(F.data.regexp(r"deny_payment_from_admin:(.+)$"))
async def deny_payment_from_admin_handler(callback: types.CallbackQuery, state: FSMContext):
    redis_key = callback.data.split("deny_payment_from_admin:")[1]