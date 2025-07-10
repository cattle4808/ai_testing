from datetime import datetime
from aiogram import Router, F, types
from asgiref.sync import sync_to_async
from django.conf import settings
from aiogram.fsm.context import FSMContext
from aiogram.filters.state import State, StatesGroup
from aiogram.exceptions import TelegramBadRequest
import math

from .. import CommandMap
from .. import bot, redis
from ..keyboards.history import inline as inline_history

from services.models import operations

user_history = Router()


def parse_dt(val: str):
    try:
        return datetime.fromisoformat(val)
    except Exception:
        return val


class HistoreState(StatesGroup):
    button = State()
    page = State()
    scripts = State()


def format_scripts_text(scripts: list) -> str:
    text = "<b>Ваши сессии:</b>\n\n"
    for s in scripts:
        start = parse_dt(s["start_at"])
        stop = parse_dt(s["stop_at"])
        text += (
            f"🆔 <code>{s['key']}</code>\n"
            f"📜 {s['script']}\n"
            f"⏱ {start} - {stop}\n"  
            f"{'💰 Оплачено' if s['is_active'] else '🚫 Не оплачено'}\n"
            f"_____________\n\n"
        )
    return text


async def render_sessions_page(message: types.Message, scripts: list, page: int):
    per_page = 5
    total_pages = math.ceil(len(scripts) / per_page)
    start_idx = page * per_page
    end_idx = start_idx + per_page

    current = scripts[start_idx:end_idx]
    text = format_scripts_text(current)

    await message.answer(
        text,
        reply_markup=inline_history.get_page_keyboard_sessions_history(page + 1, total_pages, current),
        parse_mode="HTML"
    )


@user_history.message(F.text == CommandMap.User.MY_SCRIPTS)
async def my_sessions_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state:
        await message.answer("⚠️ Завершите текущую операцию")
        return

    await state.clear()
    await state.set_state(HistoreState.button)

    my_scripts = await sync_to_async(operations.get_my_scripts)(message.from_user.id)
    if not my_scripts:
        await message.answer("❗️ У вас нет активных сессий")
        return

    await state.update_data(scripts=my_scripts, page=0)
    await render_sessions_page(message, my_scripts, 0)


@user_history.callback_query(F.data.startswith("scripts_page_"))
async def handle_scripts_page(callback: types.CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    if current_state != HistoreState.button:
        await callback.answer("⚠️ Сессия истекла", show_alert=True)
        return

    data = await state.get_data()
    scripts = data.get("scripts", [])

    if not scripts:
        await callback.answer("❌ Нет данных")
        return

    try:
        page = int(callback.data.split("_")[-1]) - 1
    except (ValueError, IndexError):
        await callback.answer("❌ Неверный формат страницы")
        return

    per_page = 5
    total_pages = math.ceil(len(scripts) / per_page)

    if page < 0 or page >= total_pages:
        await callback.answer("❌ Неверная страница")
        return

    await state.update_data(page=page)

    start_idx = page * per_page
    end_idx = start_idx + per_page
    current = scripts[start_idx:end_idx]

    text = format_scripts_text(current)

    try:
        await callback.message.edit_text(
            text,
            reply_markup=inline_history.get_page_keyboard_sessions_history(page + 1, total_pages, current),
            parse_mode="HTML"
        )
    except TelegramBadRequest as e:
        if "message is not modified" in str(e):
            await callback.answer("Данные актуальны")
        else:
            raise

    await callback.answer()


@user_history.callback_query(F.data == "scripts_page_1")
async def refresh_scripts(callback: types.CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    # if current_state != HistoreState.button:
    #     await callback.answer("⚠️ Сессия истекла", show_alert=True)
    #     return

    my_scripts = await sync_to_async(operations.get_my_scripts)(callback.from_user.id)
    if not my_scripts:
        await callback.message.edit_text("❗️ У вас нет активных сессий")
        await state.clear()
        return

    await state.update_data(scripts=my_scripts, page=0)

    per_page = 5
    total_pages = math.ceil(len(my_scripts) / per_page)
    current = my_scripts[:per_page]
    text = format_scripts_text(current)

    try:
        await callback.message.edit_text(
            text,
            reply_markup=inline_history.get_page_keyboard_sessions_history(1, total_pages, current),
            parse_mode="HTML"
        )
    except TelegramBadRequest as e:
        if "message is not modified" in str(e):
            await callback.answer("Данные актуальны")
        else:
            raise

    await callback.answer("🔄 Обновлено")


@user_history.callback_query(F.data.startswith("script_detail_"))
async def script_detail(callback: types.CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    if current_state != HistoreState.button:
        await callback.answer("⚠️ Сессия истекла", show_alert=True)
        return

    try:
        script_id = int(callback.data.split("_")[-1])
    except (ValueError, IndexError):
        await callback.answer("❌ Неверный ID скрипта")
        return

    data = await state.get_data()
    scripts = data.get("scripts", [])

    script = next((s for s in scripts if s.get('id') == script_id), None)
    if not script:
        await callback.answer("❌ Скрипт не найден")
        return

    start = parse_dt(script["start_at"])
    stop = parse_dt(script["stop_at"])

    detail_text = (
        f"<b>📋 Детали сессии</b>\n\n"
        f"🆔 <b>ID:</b> <code>{script['key']}</code>\n"
        f"📜 <b>Скрипт:</b> {script['script']}\n"
        f"⏱ <b>Время:</b> {start} - {stop}\n"
        f"💰 <b>Статус:</b> {'Оплачено' if script['is_active'] else 'Не оплачено'}\n"
    )

    if script['is_active']:
        detail_text += f"\n🔗 <b>Ссылка:</b> {settings.GET_SCRIPT_URL}/{script['script']}"

    await callback.answer(detail_text, show_alert=True)


@user_history.callback_query(F.data == "current_page")
async def current_page_info(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    page = data.get("page", 0)
    scripts = data.get("scripts", [])
    total_pages = math.ceil(len(scripts) / 5) if scripts else 1

    await callback.answer(f"📄 Страница {page + 1} из {total_pages}")