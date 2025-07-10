import json

from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from asgiref.sync import sync_to_async

from .. user import user_inline, admin_inline
from ... import redis, bot
from ... fsm.user import UserPaymentCheck

from services.models import operations


user_callback = Router()

@user_callback.callback_query(F.data == "faq")
async def show_faq(callback: types.CallbackQuery):
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
    await callback.message.delete()

    redis_key = callback.data.split("buy_script:")[1]
    raw_data = await redis.get(f"buy_script:{redis_key}")

    if not raw_data:
        return

    data = json.loads(raw_data)

    referrals = await sync_to_async(operations.get_referrals_counts)(callback.from_user.id)

    await callback.message.answer(
        f"Доступные реферралки: {len(referrals.get('unused'))}\n"
    )

    await state.set_state(UserPaymentCheck.waiting_for_img)
    await state.update_data(redis_key=redis_key)

    payment_sum = 250_000

    msg = await callback.message.answer(
        f"💳 <b>Оплата {payment_sum} сум</b>\n\n"
        f"🆔:<code>{data.get('key')}</code>\n"
        f"start_at: <code>{data.get('start_at')}</code>\n"
        f"stop_at: <code>{data.get('stop_at')}</code>\n"
        "💰 <b>Карта для перевода:</b>\n<code>5614 6805 1994 2698</code>\n"
        "Владелец: <b>UMEDJANOV.A</b>\n\n"
        "📸 После оплаты просто пришли сюда фото или скриншот чека.",
        parse_mode="HTML",
        reply_markup=user_inline.cancel_keyboard(redis_key)
    )

    data["payment_msg_id"] = msg.message_id
    data["payment_sum"] = payment_sum
    await redis.set(f"buy_script:{redis_key}", json.dumps(data))


@user_callback.callback_query(F.data.regexp(r"^cancel_payment:(.+)$"))
async def cancel_payment(callback: types.CallbackQuery):
    redis_key = callback.data.split("cancel_payment:")[1]
    await redis.delete(f"buy_script:{redis_key}")
    await callback.message.delete()
    await callback.message.answer("Оплата отменена")



@user_callback.callback_query(F.data.regexp(r"send_pay:(.+)$"))
async def send_pay(callback: types.CallbackQuery, state: FSMContext):
    redis_key = callback.data.split("send_pay:")[1]

    if not redis_key:
        await state.clear()
        return

    raw_data = await redis.get(f"buy_script:{redis_key}")

    if not raw_data:
        return

    data = json.loads(raw_data)

    admins = await sync_to_async(operations.get_admins)()

    _admins_dict = {}

    caption = (f"User_id: {data.get('user_id')}\n"
               f"user_name: {await bot.get_chat(data.get('user_id')).username}\n"
                f"🆔: <code>{data.get('key')}</code>\n\n"
                f"сумма: <b>{data.get('payment_sum')}</b>\n"
                f"start_at: <code>{data.get('start_at')}</code>\n"
                f"stop_at: <code>{data.get('stop_at')}</code>\n")

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


    await bot.edit_message_reply_markup(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=None,
        # parse_mode="HTML"
    )

    await callback.message.answer("Проверка... Подопждите идет проверка")

@user_callback.callback_query(F.data.regexp(r"resend_pay:(.+)$"))
async def recheck_pay(callback: types.CallbackQuery, state: FSMContext):
    redis_key = callback.data.split("recheck_pay:")[1]

    await callback.message.answer("Проверка...")