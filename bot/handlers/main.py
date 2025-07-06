from aiogram import Router, types, F
from aiogram.filters import CommandStart
from asgiref.sync import sync_to_async

from services.crypto import CompactReferralCipher
from .. import bot
from services.models import operations
from ..keyboards.user import reply as user_reply, inline as user_inline
from ..keyboards.admin import reply as admin_reply, inline as admin_inline

main = Router()

@main.message(CommandStart(deep_link=True))
async def start_handler(message: types.Message, command: CommandStart):
    user_id = message.from_user.id
    username = message.from_user.username or "ГОСТЬ"
    referral_code = command.args

    ref_by = None
    if referral_code:
        try:
            decrypted_id = CompactReferralCipher().decrypt_id(referral_code)
            if decrypted_id and decrypted_id != user_id:
                ref_by = decrypted_id
                await message.answer(f"Вы пришли по реферальной ссылке пользователя {ref_by}")
            elif decrypted_id == user_id:
                await message.answer("Вы не можете использовать свою собственную реферальную ссылку.")
            else:
                await message.answer("❌ Неверный или поврежденный реферальный код.")
        except Exception as e:
            await message.answer("❌ Ошибка при расшифровке реферального кода.")
            print(f"[REFERRAL ERROR] Невозможно расшифровать код '{referral_code}': {e}")

    user = await sync_to_async(operations.get_or_create_tg_user)(user_id, ref_by=ref_by)

    if await sync_to_async(operations.is_admin)(user_id):
        await message.answer("Вы администратор", reply_markup=admin_reply.main_menu())
        return

    await message.answer(f"Привет, {username}!", reply_markup=user_reply.main_menu())
