import pprint

from aiogram import Router
from aiogram import F, types
from asgiref.sync import sync_to_async
from django.conf import settings
from aiogram.fsm.context import FSMContext


from ..keyboards.user import inline as user_inline, reply as user_reply
from ..keyboards.admin import inline as admin_inline, reply as admin_reply
from .. import CommandMap
from ..fsm.user import UserPaymentCheck

from services.models import operations
from services.models import refferal

user_history = Router()

def render_script_short(script: dict) -> str:
    return (
        f"🆔 <code>{script['key']}</code>\n"
        f"Название: <b>{script['script']}</b>\n"
        f"📅 {script['start_at']} → {script['stop_at']}\n"
        f"✅ Активен: {script['is_active']} | Использован: {script['used']}/{script['max_usage']}"
    )

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_pagination_keyboard(page: int, total: int, per_page: int):
    max_page = (total + per_page - 1) // per_page
    buttons = []

    if page > 1:
        buttons.append(InlineKeyboardButton("⬅️", callback_data=f"page:{page-1}"))
    buttons.append(InlineKeyboardButton(f"{page}/{max_page}", callback_data="noop"))
    if page < max_page:
        buttons.append(InlineKeyboardButton("➡️", callback_data=f"page:{page+1}"))

    return InlineKeyboardMarkup(inline_keyboard=[buttons])


@user_history.message(F.text == CommandMap.User.MY_SCRIPTS)
async def my_shops(message: types.Message, state: FSMContext):
    state_name = await state.get_state()
    if state_name == UserPaymentCheck.waiting_for_img:
        try:
            await message.delete()
        except:
            pass
        await message.answer("⛔ Сначала завершите текущую оплату — отправьте фото чека.")
        return

    user_id = message.from_user.id

    await message.answer(
        "<b>📂 Мои скрипты</b>\n\n"
        "Здесь вы можете управлять своими скриптами.\n"
    )

    my_scripts = await sync_to_async(operations.get_my_scripts)(user_id)

    pprint.pprint(my_scripts, indent=4)

@user_history.callback_query(F.data.regexp(r'^page:(\d+)$'))
async def change_script_page(callback: types.CallbackQuery):
    page = int(callback.data.split(":")[1])
    user_id = callback.from_user.id
    scripts_data = operations.get_my_scripts_with_pagination(user_id=user_id, page=page)

    text = "\n\n".join([render_script_short(s) for s in scripts_data['scripts']]) or "❗️Нет скриптов"
    markup = get_pagination_keyboard(page, scripts_data['total'], scripts_data['per_page'])

    await callback.message.edit_text(text, reply_markup=markup, parse_mode="HTML")
    await callback.answer()
