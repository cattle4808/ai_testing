from aiogram import Router, F, types
from asgiref.sync import sync_to_async
from django.conf import settings
from aiogram.fsm.context import FSMContext
from aiogram.filters.state import State, StatesGroup


from .. import CommandMap
from .. import bot, redis
from .. keyboards.history import inline as inline_history

from services.models import operations

user_history = Router()


def parse_dt(val: str):
    try:
        return datetime.fromisoformat(val)
    except Exception:
        return val

# @user_history.message(CommandMap.User.MY_SCRIPTS)
# async def my_scripts(message: types.Message, state: FSMContext):
#
#     user_id = message.from_user.id
#
#     scripts_data = await sync_to_async(operations.get_my_scripts_with_pagination)(user_id, page=1, per_page=5)
#
#     if not scripts_data['scripts']:
#         await message.answer(
#             f"<b>{CommandMap.User.MY_SCRIPTS}</b>\n\n"
#             "❌ У вас пока нет скриптов.\n"
#             "Купите скрипт, чтобы он появился здесь."
#         )
#         return

class HistoreState(StatesGroup):
    button = State()
    page = State()
    scripts = State()

async def render_sessions_page(message: types.Message, scripts: list, page: int):
    per_page = 5
    max_page = (len(scripts) - 1) // per_page
    start_idx = page * per_page
    end_idx = start_idx + per_page

    current = scripts[start_idx:end_idx]
    text = "<b>Ваши сессии:</b>\n\n"
    for s in current:
        text += (
            f"🆔 <code>{s['key']}</code>\n"
            f"📜 {s['script']}\n"
            f"⏱ {s['start_at']} - {s['stop_at']}\n"
            f"{'💰 Оплачено' if s['is_paid'] else '🚫 Не оплачено'}\n"
            f"_____________\n\n"
        )

    await message.answer(
        text,
        reply_markup=inline_history.get_page_keyboard_sessions_history(page, max_page),
        parse_mode="HTML"
    )

@user_history.message(F.text == CommandMap.User.MY_SCRIPTS)
async def my_sessions_handler(message: types.Message, state: FSMContext):
    await state.clear()
    await state.set_state(HistoreState.button)

    my_scripts = await sync_to_async(operations.get_my_scripts)(message.from_user.id)
    if not my_scripts:
        await message.answer("❗️ У вас нет активных сессий")
        return

    await state.update_data(scripts=my_scripts, page=0)
    await render_sessions_page(message, my_scripts, 0)

@user_history.callback_query(F.data.in_(["sessions_prev", "sessions_next"]))
async def paginate_sessions(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    scripts = data.get("scripts", [])
    page = data.get("page", 0)

    per_page = 5
    max_page = (len(scripts) - 1) // per_page

    if callback.data == "sessions_next" and page < max_page:
        page += 1
    elif callback.data == "sessions_prev" and page > 0:
        page -= 1

    await state.update_data(page=page)

    start_idx = page * per_page
    end_idx = start_idx + per_page
    current = scripts[start_idx:end_idx]

    text = "<b>Ваши сессии:</b>\n\n"
    for s in current:
        start = parse_dt(s["start_at"])
        stop = parse_dt(s["stop_at"])
        text += (
            f" <code>{s['key']}</code>\n"
            f"📜 {s['script']}\n"
            f"⏱ {start} - {start}\n"
            f"{'💰 Оплачено' if s['is_active'] else '🚫 Не оплачено'}\n"
            f"_____________\n\n"
        )
    await callback.message.edit_text(
        text,
        reply_markup=inline_history.get_page_keyboard_sessions_history(page, max_page, current),
        parse_mode="HTML"
    )
    await callback.answer()


