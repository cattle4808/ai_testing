from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from asgiref.sync import sync_to_async

from services.models import operations
from ... import redis, bot

admin_callback = Router()


@admin_callback.callback_query(F.data.regexp(r"allow_payment_from_admin:(.+)$"))
async def allow_payment_from_admin_handler(callback: types.CallbackQuery, state: FSMContext):
    redis_key = callback.data.split("allow_payment_from_admin:")[1]
    raw_data = redis.get(f"redis_key:{redis_key}")

    key = raw_data.get("key")

    await sync_to_async(operations.change_script_status)(key, True)
    await bot.delete_message(
        chat_id=callback.from_user.id,
        message_id=raw_data.get("m")
    )

@admin_callback.callback_query(F.data.regexp(r"deny_payment_from_admin:(.+)$"))
async def deny_payment_from_admin_handler(callback: types.CallbackQuery, state: FSMContext):
    redis_key = callback.data.split("deny_payment_from_admin:")[1]