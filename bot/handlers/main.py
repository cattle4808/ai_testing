from aiogram import Router, types, F
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from asgiref.sync import sync_to_async

from services.crypto import CompactReferralCipher
from services.models import operations
from ..keyboards.user import reply as user_reply, inline as user_inline
from ..keyboards.admin import reply as admin_reply, inline as admin_inline
from .. import bot
from ..filters import police


main = Router()

@main.message(CommandStart())
async def start_handler(message: types.Message, command: CommandStart):
    await message.answer(
        "<b>🎓 Решение для прохождения тестов на Uchi, РЭШ, Foxford и др</b>\n\n"
        "Сервис показывает готовые ответы во время прохождения заданий.\n"
        "Работает прямо в браузере — без установки.\n\n"
        "✅ <b>Поддержка всех классов и предметов</b>\n"
        "✅ <b>Подсказки появляются в том же окне, где и тест</b>\n"
        "✅ <b>Удобный выбор времени — активируется по вашему расписанию</b>\n"
        "✅ <b>Поддержка всегда на связи</b>\n\n"
        "💸 <i>Пригласи друга — получи скидку.</i>",
        parse_mode="HTML"
    )

    user_id = message.from_user.id
    username = message.from_user.username or "Гость"
    referral_code = command.args
    ref_by = None

    if referral_code:
        try:
            ref_by = CompactReferralCipher().decrypt_id(referral_code)
            if ref_by == user_id or ref_by is None:
                ref_by = None
            else:
                await message.answer("👥 Вы пришли по приглашению.")
        except Exception as e:
            ref_by = None
            print(f"[REFERRAL ERROR] '{referral_code}': {e}")
    # else:
    #     await message.answer()

    user = await sync_to_async(operations.get_or_create_tg_user)(user_id, ref_by)

    if not user.get("police", False):
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ Принять политику", callback_data="accept_policy_main")]
        ])

        await bot.send_document(
            chat_id=user_id,
            document="BQACAgIAAxkBAAIW_2iDiRrkxq2C4XoGwk2tHwZecaoQAAJndwACx90YSJrHnFqsl8QMNgQ",
            caption="<b>🛡️ Прежде чем начать, пожалуйста, ознакомьтесь и примите политику использования.</b>\n\n"
                    "Нажмите кнопку ниже, чтобы подтвердить согласие.",
            parse_mode="HTML",
            reply_markup=kb
        )
        return

    if await sync_to_async(operations.is_admin)(user_id):
        await message.answer("✅ Вы вошли как администратор", reply_markup=admin_reply.main_menu())
    else:
        await message.answer(f"Привет, {username}!", reply_markup=user_reply.main_menu())


@main.callback_query(F.data == "accept_policy_main")
async def accept_policy_handler(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    username = callback.from_user.username or "Гость"

    await sync_to_async(operations.set_police)(user_id, True)

    await callback.message.delete()
    await callback.answer("✅ Политика принята")

    if await sync_to_async(operations.is_admin)(user_id):
        await callback.message.answer("✅ Вы вошли как администратор", reply_markup=admin_reply.main_menu())
    else:
        await callback.message.answer(f"Привет, {username}!", reply_markup=user_reply.main_menu())
