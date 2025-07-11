import json
from aiogram import Router, F, types
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from asgiref.sync import sync_to_async
from django.conf import settings

from services.models import operations
from ... import redis, bot

admin_callback = Router()


@admin_callback.callback_query(F.data.regexp(r"allow_payment_from_admin:(.+)$"))
async def allow_payment_from_admin_handler(callback: types.CallbackQuery, state: FSMContext):
    redis_key = callback.data.split("allow_payment_from_admin:")[1]
    raw_data = json.loads(await redis.get(f"buy_script:{redis_key}"))

    key = raw_data.get("key")
    change_script = await sync_to_async(operations.change_script_status)(key, True)

    referrals_bonus_count = raw_data.get("referrals_count")

    if referrals_bonus_count:
        for _ in referrals_bonus_count:
            await sync_to_async(operations.change_status_referral_by_id)(
                referral_id=_.get("id"),
                status=True
            )

    user_message_text = (
        f"✅ Оплата подтверждена\n\n"
        f"Ваша оплата успешно получена и подтверждена.\n"
        f"Решение будет автоматически активировано в указанный промежуток времени:\n\n"
        f"🆔: <code>{raw_data.get('key')}</code>\n\n"
        f"⏱️ Начало: {change_script.get('start_at')}\n"
        f"⏱️ Окончание: {change_script.get('stop_at')}\n\n"
        f"🔗 Ссылка на решение:\n"
        f"<code>javascript:import('{settings.GET_SCRIPT_JS}/{change_script.get('script')}')</code>\n\n"
        f"📌 Пожалуйста, будьте на связи в этот период — система включится автоматически."
    )
    await bot.send_photo(
        chat_id=raw_data.get("user_id"),
        photo=raw_data.get("file_id"),
        caption=user_message_text,
        parse_mode="HTML"
    )

    testing_script_name = f"testing_{raw_data.get('script')}"
    testing_script = await sync_to_async(operations.create_testing_script)(testing_script_name)
    testing_block = (
        f"🧪 <b>Тестовое решение:</b>\n"
        f"🆔: <code>{testing_script.get('key')}</code>\n"
        f"⏱️ Срок действия: <code>{testing_script.get('start_at')}</code> — <code>{testing_script.get('stop_at')}</code>\n"
        f"🔗 <b>Ссылка:</b> <code>javascript:import('{settings.GET_SCRIPT_JS}/{testing_script.get('script')}')</code>\n\n"
        f"Можно использовать для предварительной проверки работы системы и интерфейса."
    )

    await bot.send_message(
        chat_id=raw_data.get("user_id"),
        text=testing_block,
        parse_mode="HTML"
    )


    chat = await bot.get_chat(raw_data.get('user_id'))
    user_name = chat.username or 'скрыт'

    caption = (
        f"User_id: {raw_data.get('user_id')}\n"
        f"user_name: {user_name}\n"
        f"🆔: <code>{raw_data.get('key')}</code>\n\n"
        f"💵 Сумма: <b>{raw_data.get('payment_sum')}</b>\n"
        f"⏱️ С:  <code>{raw_data.get('start_at')}</code>\n"
        f"⏱️ До: <code>{raw_data.get('stop_at')}</code>\n\n"
        f"✅ <b>Оплата подтверждена</b>"
    )

    for admin, msg_id in raw_data.get("admins").items():
        try:
            await bot.edit_message_caption(
                chat_id=int(admin),
                message_id=msg_id,
                caption=caption,
                reply_markup=None,
                parse_mode="HTML"
            )
        except TelegramBadRequest as e:
            if "message is not modified" in str(e):
                pass
            else:
                raise


    if raw_data.get("referred_by"):
        await sync_to_async(operations.add_to_referral)(
            inviter_user_id=raw_data.get("referred_by"),
            invited_user_id=raw_data.get("user_id")
        )

    try:
        await bot.delete_message(
            chat_id=raw_data.get("user_id"),
            message_id=raw_data.get("payment_msg_id")
        )
    except:
        pass

    try:
        await bot.delete_message(
            chat_id=raw_data.get("user_id"),
            message_id=raw_data.get("send_payment_msg_id")
        )
    except:
        pass
    await state.clear()
    await redis.delete(f"buy_script:{redis_key}")


@admin_callback.callback_query(F.data.regexp(r"deny_payment_from_admin:(.+)$"))
async def deny_payment_from_admin_handler(callback: types.CallbackQuery, state: FSMContext):
    redis_key = callback.data.split("deny_payment_from_admin:")[1]
    raw_data = json.loads(await redis.get(f"buy_script:{redis_key}"))
    key = raw_data.get("key")

    referrals_bonus_count = raw_data.get("referrals_count")
    if referrals_bonus_count:
        for _ in referrals_bonus_count:
            await sync_to_async(operations.change_status_referral_by_id)(
                referral_id=_.get("id"),
                status=False
            )

    user_message_text = (
        f"❌ Оплата отклонена\n\n"
        f"К сожалению, ваша оплата не была подтверждена администратором.\n"
        f"Если вы считаете, что произошла ошибка — свяжитесь с поддержкой или админом вручную.\n\n"
        f"🆔: <code>{raw_data.get('key')}</code>\n\n"
        f"💵 Сумма: <b>{raw_data.get('payment_sum')}</b>\n"
        f"⏱️ С: <code>{raw_data.get('start_at')}</code>\n"
        f"⏱️ До: <code>{raw_data.get('stop_at')}</code>\n\n"
    )

    await bot.send_photo(
        chat_id=raw_data.get("user_id"),
        photo=raw_data.get("file_id"),
        caption=user_message_text,
        parse_mode="HTML"
    )

    chat = await bot.get_chat(raw_data.get('user_id'))
    user_name = chat.username or 'скрыт'
    caption_2 = (
        f"User_id: {raw_data.get('user_id')}\n"
        f"user_name: {user_name}\n"
        f"🆔: <code>{raw_data.get('key')}</code>\n\n"
        f"💵 Сумма: <b>{raw_data.get('payment_sum')}</b>\n"
        f"⏱️ С:  <code>{raw_data.get('start_at')}</code>\n"
        f"⏱️ До: <code>{raw_data.get('stop_at')}</code>\n\n"
        f"❌ <b>Оплата отклонена </b>"
    )

    for admin, msg_id in raw_data.get("admins").items():
        try:
            await bot.edit_message_caption(
                chat_id=int(admin),
                message_id=msg_id,
                caption=caption_2,
                parse_mode="HTML",
                reply_markup=None
            )
        except TelegramBadRequest as e:
            if "message is not modified" in str(e):
                pass
            else:
                raise

    try:
        await bot.delete_message(
            chat_id=raw_data.get("user_id"),
            message_id=raw_data.get("payment_msg_id")
        )
    except:
        pass

    try:
        await bot.delete_message(
            chat_id=raw_data.get("user_id"),
            message_id=raw_data.get("send_payment_msg_id")
        )
    except:
        pass

    await state.clear()
    await redis.delete(f"buy_script:{redis_key}")
