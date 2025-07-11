import json
from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from asgiref.sync import sync_to_async
from django.conf import settings

from .. user import user_inline, admin_inline
from ... import redis, bot
from ... fsm.user import UserPaymentCheck

from services.models import operations


user_callback = Router()

@user_callback.callback_query(F.data == "faq")
async def show_faq(callback: types.CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    if current_state:
        await callback.answer("⚠️ Завершите текущую операцию", show_alert=True)
        return

    await callback.answer()

    text = (
        "<b>📚 Популярные вопросы</b>\n\n"

        "1. 👥 <b>Как работает реферальная программа?</b>\n"
        "Вы приглашаете людей. Если кто-то из них совершит покупку, вы получите скидку 25 000 сум. "
        "Максимальная скидка — 125 000 сум на одну покупку.\n\n"

        "2. 🕒 <b>Когда активируется скрипт?</b>\n"
        "Скрипт будет работать ровно 2 часа с выбранного вами времени. "
        "Например, если вы выбрали 14:30 — скрипт будет активен с 14:30 до 16:30.\n\n"

        "3. 💰 <b>Как происходит оплата?</b>\n"
        "После выбора времени вы получите сумму. Оплатите удобным способом и отправьте скрин чека администратору для активации скрипта.\n\n"

        "4. 🚫 <b>Можно ли вернуть деньги?</b>\n"
        "Нет. Возврат средств не предусмотрен. Перед оплатой внимательно проверьте всё.\n\n"

        "5. 🔐 <b>Насколько это безопасно?</b>\n"
        "Мы используем Telegram WebApp. Данные надежно защищены, и ничего лишнего не сохраняется.\n\n"

        "6. 📩 <b>К кому обращаться с вопросами?</b>\n"
        "Свяжитесь с админом: @AFT_Admin1"
    )

    await callback.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=user_inline.back_support()
    )


@user_callback.callback_query(F.data == "back_to_support")
async def support(callback: types.CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(
        "<b>🛠 Служба поддержки</b>\n\n"
        "Мы ценим ваше доверие и всегда готовы помочь.\n"
        "Если у вас возникли сложности — обращайтесь напрямую. "
        "Мы ответим максимально быстро и с заботой о каждом пользователе.\n\n"
        "🔐 <b>Ваша безопасность</b> — наш главный приоритет.\n"
        "🎯 <b>Ваша уверенность</b> — наша ответственность.\n\n",
        parse_mode="HTML",
        reply_markup=user_inline.support()
    )


@user_callback.callback_query(F.data.regexp(r"^buy_script:(.+)$"))
async def buy(callback: types.CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
    except Exception as e:
        print(e)

    redis_key = callback.data.split("buy_script:")[1]
    raw_data = await redis.get(f"buy_script:{redis_key}")

    if not raw_data:
        return

    data = json.loads(raw_data)

    referrals = await sync_to_async(operations.get_referrals_counts)(callback.from_user.id)
    referrals_list = referrals.get('unused', [])[:5]
    referrals_count = len(referrals_list)

    base_price = settings.SCRIPT_BASE_PRICE
    discount = referrals_count * settings.REWERD_PER_REFFERAL
    payment_sum = max(base_price - discount, 0)

    referral_note = (
        f"<s>{base_price} сум</s> → <b>{payment_sum} сум</b>\n"
        if referrals_count > 0 else
        f"<b>{payment_sum} сум</b>\n"
    )

    await state.set_state(UserPaymentCheck.waiting_for_img)
    await state.update_data(redis_key=redis_key)

    msg = await callback.message.answer(
        f"💳 К оплате: {referral_note}\n"
        f"🆔 <code>{data.get('key')}</code>\n"
        f"⏱ <code>{data.get('start_at')}</code>\n"
        f"⏳ <code>{data.get('stop_at')}</code>\n\n"
        "💰 <b>Карта для перевода:</b>\n<code>9860 3501 4146 8917</code>\n"
        "Владелец: <b>DANIIL TERGALINSKIY</b>\n\n"
        "<b>📸 После оплаты просто пришли сюда фото или скриншот чека.</b>",
        parse_mode="HTML",
        reply_markup=user_inline.cancel_keyboard(redis_key)
    )

    data["payment_msg_id"] = msg.message_id
    data["payment_sum"] = payment_sum
    data["referrals_count"] = referrals_list
    await redis.set(f"buy_script:{redis_key}", json.dumps(data))


@user_callback.callback_query(F.data.regexp(r"^cancel_payment:(.+)$"))
async def cancel_payment(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    redis_key = callback.data.split("cancel_payment:")[1]

    raw_data = await redis.get(f"buy_script:{redis_key}")
    if not raw_data:
        return

    data = json.loads(raw_data)

    for msg_key in ("payment_msg_id", "send_payment_msg_id"):
        msg_id = data.get(msg_key)
        if msg_id:
            try:
                await bot.delete_message(chat_id=data.get("user_id"), message_id=msg_id)
            except:
                pass

    try:
        await callback.message.delete()
    except:
        pass

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

    await callback.message.answer("❌ <b>Оплата отменена</b>", parse_mode="HTML")



@user_callback.callback_query(F.data.regexp(r"send_pay:(.+)$"))
async def send_pay(callback: types.CallbackQuery, state: FSMContext):
    redis_key = callback.data.split("send_pay:")[1]

    if not redis_key:
        await state.clear()
        return

    raw_data = await redis.get(f"buy_script:{redis_key}")

    if not raw_data:
        await state.clear()
        return

    data = json.loads(raw_data)

    referral_list = data.get("referrals_count")
    if referral_list:
        for ref in referral_list:
            await sync_to_async(operations.change_status_referral_by_id)(
                referral_id=ref.get("id"),
                status=False
            )

    admins = await sync_to_async(operations.get_admins)()

    _admins_dict = {}

    user_id = data.get('user_id')
    user_info = await bot.get_chat(user_id)
    username = user_info.username or "скрыт"

    caption = (
        f"👤 <b>User ID:</b> <code>{user_id}</code>\n"
        f"🔗 <b>Username:</b> @{username if username != 'скрыт' else 'скрыт'}\n"
        f"🆔 <b>Ключ:</b> <code>{data.get('key')}</code>\n"
        f"💰 <b>Сумма:</b> {data.get('payment_sum')} сум\n"
        f"⏱ <b>Начало:</b> <code>{data.get('start_at')}</code>\n"
        f"⏳ <b>Конец:</b> <code>{data.get('stop_at')}</code>"
    )

    for admin in admins:
        admin_id = admin.get("user")
        message = await callback.bot.send_photo(
            chat_id=admin_id,
            photo=data.get("file_id"),
            caption=caption,
            reply_markup=admin_inline.check_payment(redis_key),
            parse_mode="HTML"
        )
        _admins_dict[str(admin_id)] = message.message_id

    data["admins"] = _admins_dict
    await redis.set(f"buy_script:{redis_key}", json.dumps(data))

    try:
        await bot.edit_message_reply_markup(
            chat_id=callback.from_user.id,
            message_id=callback.message.message_id,
            reply_markup=None,
        )
    except:
        pass

    await callback.message.answer(
        "🔎 <b>Платёж отправлен на проверку</b>\n\n"
        "Пожалуйста, подождите — администратор проверит чек и подтвердит активацию.",
        parse_mode="HTML"
    )

@user_callback.callback_query(F.data.regexp(r"^resend_pay:(.+)$"))
async def recheck_pay(callback: types.CallbackQuery, state: FSMContext):
    redis_key = callback.data.split("resend_pay:")[1]

    await callback.message.answer(
        "📤 <b>Вы можете отправить новый чек</b>\n\n"
        "Просто пришлите сюда новое фото или скриншот оплаты.",
        parse_mode="HTML"
    )

    await state.set_state(UserPaymentCheck.waiting_for_img)
    await state.update_data(redis_key=redis_key)
