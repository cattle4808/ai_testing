from aiogram import Router, types
from aiogram.filters import CommandStart
from asgiref.sync import sync_to_async

from services.crypto import CompactReferralCipher
from services.models import operations
from ..keyboards.user import reply as user_reply, inline as user_inline
from ..keyboards.admin import reply as admin_reply, inline as admin_inline


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
            if ref_by == user_id:
                ref_by = None
            elif ref_by is None:
                ref_by = None
            else:
                await message.answer("👥 Привет! Вы пришли по приглашению.")
        except Exception as e:
            ref_by = None
            print(f"[REFERRAL ERROR] '{referral_code}': {e}")
    else:
        await message.answer("👋 Привет! Добро пожаловать!")

    user = await sync_to_async(operations.get_or_create_tg_user)(user_id, ref_by)

    if await sync_to_async(operations.is_admin)(user_id):
        await message.answer("✅ Вы вошли как администратор", reply_markup=admin_reply.main_menu())
    else:
        await message.answer(f"Привет, {username}!", reply_markup=user_reply.main_menu())



