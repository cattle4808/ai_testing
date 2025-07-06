from aiogram import Router, types
from aiogram.filters import CommandStart
from asgiref.sync import sync_to_async

from services.crypto import CompactReferralCipher
from services.models import operations
from ..keyboards.user import reply as user_reply, inline as user_inline
from ..keyboards.admin import reply as admin_reply, inline as admin_inline

main = Router()

#
# @main.message(CommandStart(deep_link=True))
# async def start_handler(message: types.Message, command: CommandStart):
#     user_id = message.from_user.id
#     username = message.from_user.username or "Гость"
#     referral_code = command.args
#
#     ref_by = None
#     if referral_code:
#         try:
#             ref_by = CompactReferralCipher().decrypt_id(referral_code)
#             if ref_by is None:
#                 await message.answer("❌ Неверный или поврежденный реферальный код.")
#             elif ref_by == user_id:
#                 await message.answer("Вы не можете использовать свою собственную реферальную ссылку.")
#                 ref_by = None
#             else:
#                 await message.answer(f"Вы пришли по реферальной ссылке пользователя {ref_by}")
#         except Exception as e:
#             await message.answer("❌ Ошибка при расшифровке кода.")
#             print(f"[REFERRAL ERROR] '{referral_code}': {e}")
#     else:
#         await message.answer("👋 Привет! Добро пожаловать!")
#
#     user = await sync_to_async(operations.get_or_create_tg_user)(user_id, ref_by=ref_by)
#
#     if await sync_to_async(operations.is_admin)(user_id):
#         await message.answer("Вы вошли как администратор", reply_markup=admin_reply.main_menu())
#         return
#
#     await message.answer(f"Привет, {username}!", reply_markup=user_reply.main_menu())


@main.message(CommandStart())
async def start_handler(message: types.Message, command: CommandStart):
    user_id = message.from_user.id
    username = message.from_user.username or "Гость"
    referral_code = command.args

    ref_by = None
    if referral_code:
        try:
            ref_by = CompactReferralCipher().decrypt_id(referral_code)
            if ref_by is None:
                await message.answer("❌ Неверный или поврежденный реферальный код.")
            elif ref_by == user_id:
                await message.answer("Вы не можете использовать свою собственную реферальную ссылку.")
                ref_by = None
            else:
                await message.answer(f"Вы пришли по реферальной ссылке пользователя {ref_by}")
        except Exception as e:
            await message.answer("❌ Ошибка при расшифровке кода.")
            print(f"[REFERRAL ERROR] '{referral_code}': {e}")
    else:
        await message.answer("👋 Привет! Добро пожаловать!")

    user = await sync_to_async(operations.get_or_create_tg_user)(user_id, ref_by)
    await message.answer(str(user))

    if await sync_to_async(operations.is_admin)(user_id):
        await message.answer("Вы вошли как администратор", reply_markup=admin_reply.main_menu())
        return

    await message.answer(f"Привет, {username}!", reply_markup=user_reply.main_menu())
