import pprint

from aiogram import Router
from aiogram import F, types
from asgiref.sync import sync_to_async
from django.conf import settings
from aiogram.fsm.context import FSMContext
from django.forms import model_to_dict
from django.utils import timezone

from ..keyboards.user import inline as user_inline, reply as user_reply
from ..keyboards.admin import inline as admin_inline, reply as admin_reply
from .. import CommandMap
from ..fsm.user import UserPaymentCheck
from api.v1 import models
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from datetime import datetime

from services.models import operations
from services.models import refferal

user_history = Router()

import logging
import traceback

logger = logging.getLogger(__name__)

def catch_error(error_id):
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(f"[{error_id}] Exception in {func.__name__}: {e}")
                logger.debug(traceback.format_exc())
                return {"error": error_id}
        return wrapper
    return decorator

class ScriptsPagination:
    """Класс для управления пагинацией скриптов"""

    @staticmethod
    def get_status_emoji(script_data: dict) -> str:
        """Получить эмодзи статуса скрипта"""
        if script_data.get('is_active'):
            return "🟢"
        else:
            return "🔴"

    @staticmethod
    def format_datetime(dt) -> str:
        """Форматировать дату и время"""
        if dt is None:
            return "Не задано"
        if isinstance(dt, str):
            return dt
        return dt.strftime("%d.%m.%Y %H:%M")

    @staticmethod
    def get_script_short_info(script_data: dict, index: int) -> str:
        """Получить краткую информацию о скрипте"""
        status = ScriptsPagination.get_status_emoji(script_data)
        usage_percent = (script_data.get('used', 0) / script_data.get('max_usage', 1)) * 100

        return (
            f"{index}. {status} <b>{script_data.get('script', 'Неизвестно')}</b>\n"
            f"   📊 Использовано: {script_data.get('used', 0)}/{script_data.get('max_usage', 0)} ({usage_percent:.1f}%)\n"
            f"   ⏰ До: {ScriptsPagination.format_datetime(script_data.get('stop_at'))}\n"
        )

    @staticmethod
    def create_pagination_keyboard(current_page: int, total_pages: int, scripts_on_page: list) -> InlineKeyboardMarkup:
        """Создать клавиатуру для пагинации"""
        builder = InlineKeyboardBuilder()

        # Кнопки для выбора конкретного скрипта (1-5)
        script_buttons = []
        for i, script in enumerate(scripts_on_page, 1):
            script_buttons.append(
                InlineKeyboardButton(
                    text=f"{i}",
                    callback_data=f"script_detail_{script['id']}"
                )
            )

        # Добавляем кнопки скриптов в один ряд
        if script_buttons:
            builder.row(*script_buttons)

        # Кнопки навигации
        nav_buttons = []

        # Кнопка "Предыдущая"
        if current_page > 1:
            nav_buttons.append(
                InlineKeyboardButton(
                    text="⬅️ Назад",
                    callback_data=f"scripts_page_{current_page - 1}"
                )
            )

        # Информация о текущей странице
        nav_buttons.append(
            InlineKeyboardButton(
                text=f"{current_page}/{total_pages}",
                callback_data="current_page"
            )
        )

        # Кнопка "Следующая"
        if current_page < total_pages:
            nav_buttons.append(
                InlineKeyboardButton(
                    text="Вперед ➡️",
                    callback_data=f"scripts_page_{current_page + 1}"
                )
            )

        # Добавляем навигационные кнопки
        if nav_buttons:
            builder.row(*nav_buttons)

        # Кнопка "Обновить"
        builder.row(
            InlineKeyboardButton(
                text="🔄 Обновить",
                callback_data="scripts_page_1"
            )
        )

        return builder.as_markup()

    @staticmethod
    def create_script_detail_keyboard(script_id: int, is_active: bool = False) -> InlineKeyboardMarkup:
        """Создать клавиатуру для детального просмотра скрипта"""
        builder = InlineKeyboardBuilder()

        builder.row(
            InlineKeyboardButton(
                text="📋 Копировать ключ",
                callback_data=f"copy_key_{script_id}"
            )
        )

        # Кнопка активации/деактивации
        if is_active:
            builder.row(
                InlineKeyboardButton(
                    text="⏸️ Деактивировать",
                    callback_data=f"deactivate_script_{script_id}"
                )
            )
        else:
            builder.row(
                InlineKeyboardButton(
                    text="▶️ Активировать",
                    callback_data=f"activate_script_{script_id}"
                )
            )

        builder.row(
            InlineKeyboardButton(
                text="🔄 Обновить статус",
                callback_data=f"refresh_script_{script_id}"
            ),
            InlineKeyboardButton(
                text="🗑️ Удалить",
                callback_data=f"delete_script_{script_id}"
            )
        )

        builder.row(
            InlineKeyboardButton(
                text="⬅️ Назад к списку",
                callback_data="scripts_page_1"
            )
        )

        return builder.as_markup()


# Operations functions
@catch_error("ERR_GET_MY_SCRIPTS_WITH_PAGINATION")
def get_my_scripts_with_pagination(user_id: int, page: int = 1, per_page: int = 5) -> dict:
    """Получить скрипты пользователя с пагинацией"""
    offset = (page - 1) * per_page
    queryset = models.IdScript.objects.filter(owner__user=user_id).order_by("-created_at")
    total = queryset.count()
    scripts = queryset[offset:offset + per_page]

    script_list = [
        model_to_dict(script, fields=[
            'id', 'script', 'key', 'script_type', 'fingerprint',
            'start_at', 'stop_at', 'is_active', 'used',
            'max_usage', 'first_activate', 'first_seen'
        ]) for script in scripts
    ]

    return {
        "total": total,
        "page": page,
        "per_page": per_page,
        "scripts": script_list
    }

@catch_error("ERR_GET_SCRIPT_BY_ID")
def get_script_by_id(script_id: int) -> dict:
    """Получить скрипт по ID"""
    try:
        script = models.IdScript.objects.get(id=script_id)
        return model_to_dict(script, fields=[
            'id', 'script', 'key', 'script_type', 'fingerprint',
            'start_at', 'stop_at', 'is_active', 'used',
            'max_usage', 'first_activate', 'first_seen'
        ])
    except models.IdScript.DoesNotExist:
        return None

@catch_error("ERR_ACTIVATE_SCRIPT")
def activate_script(script_id: int, user_id: int) -> dict:
    """Активировать скрипт"""
    try:
        script = models.IdScript.objects.get(id=script_id, owner__user=user_id)

        # Проверяем, можно ли активировать скрипт
        if script.is_active:
            return {'success': False, 'error': 'Скрипт уже активен'}

        # Проверяем время действия
        current_time = timezone.now()
        if current_time < script.start_at:
            return {'success': False, 'error': 'Время начала действия скрипта еще не наступило'}

        if current_time > script.stop_at:
            return {'success': False, 'error': 'Время действия скрипта истекло'}

        # Проверяем лимит использования
        if script.used >= script.max_usage:
            return {'success': False, 'error': 'Достигнут лимит использования скрипта'}

        # Активируем скрипт
        script.is_active = True
        if not script.first_activate:
            script.first_activate = current_time
        script.save()

        return {'success': True}

    except models.IdScript.DoesNotExist:
        return {'success': False, 'error': 'Скрипт не найден'}
    except Exception as e:
        return {'success': False, 'error': str(e)}

@catch_error("ERR_DEACTIVATE_SCRIPT")
def deactivate_script(script_id: int, user_id: int) -> dict:
    """Деактивировать скрипт"""
    try:
        script = models.IdScript.objects.get(id=script_id, owner__user=user_id)

        if not script.is_active:
            return {'success': False, 'error': 'Скрипт уже неактивен'}

        script.is_active = False
        script.save()

        return {'success': True}

    except models.IdScript.DoesNotExist:
        return {'success': False, 'error': 'Скрипт не найден'}
    except Exception as e:
        return {'success': False, 'error': str(e)}


# Обработчик ReplyKeyboard кнопки "Мои покупки/скрипты"
@user_history.message(F.text.in_(["📂 Мои покупки", "📂 Мои скрипты", "Мои покупки", "Мои скрипты"]))
async def my_purchases_handler(message: types.Message, state: FSMContext):
    """Обработчик кнопки 'Мои покупки' из ReplyKeyboard"""
    await my_scripts(message, state)

# Обработчик основной команды
@user_history.message(F.text == CommandMap.User.MY_SCRIPTS)
async def my_scripts(message: types.Message, state: FSMContext):
    """Отображение списка скриптов с пагинацией"""
    state_name = await state.get_state()
    if state_name == UserPaymentCheck.waiting_for_img:
        try:
            await message.delete()
        except:
            pass
        await message.answer("⛔ Сначала завершите текущую оплату — отправьте фото чека.")
        return

    user_id = message.from_user.id

    # Получаем данные с пагинацией
    scripts_data = await sync_to_async(get_my_scripts_with_pagination)(user_id, page=1, per_page=5)

    if not scripts_data['scripts']:
        await message.answer(
            "📂 <b>Мои скрипты</b>\n\n"
            "❌ У вас пока нет скриптов.\n"
            "Купите скрипт, чтобы он появился здесь."
        )
        return

    # Формируем сообщение
    scripts_text = "📂 <b>Мои скрипты</b>\n\n"

    for i, script in enumerate(scripts_data['scripts'], 1):
        scripts_text += ScriptsPagination.get_script_short_info(script, i)
        scripts_text += "\n"

    scripts_text += f"📄 Показано: {len(scripts_data['scripts'])} из {scripts_data['total']}"

    # Создаем клавиатуру
    total_pages = (scripts_data['total'] + scripts_data['per_page'] - 1) // scripts_data['per_page']
    keyboard = ScriptsPagination.create_pagination_keyboard(
        current_page=1,
        total_pages=total_pages,
        scripts_on_page=scripts_data['scripts']
    )

    await message.answer(scripts_text, reply_markup=keyboard)

# Обработчик переключения страниц
@user_history.callback_query(F.data.startswith("scripts_page_"))
async def handle_scripts_page(callback: types.CallbackQuery, state: FSMContext):
    """Обработка переключения страниц"""
    page = int(callback.data.split("_")[-1])
    user_id = callback.from_user.id

    # Получаем данные для нужной страницы
    scripts_data = await sync_to_async(get_my_scripts_with_pagination)(user_id, page=page, per_page=5)

    if not scripts_data['scripts']:
        await callback.answer("❌ Нет скриптов на этой странице")
        return

    # Формируем сообщение
    scripts_text = "📂 <b>Мои скрипты</b>\n\n"

    for i, script in enumerate(scripts_data['scripts'], 1):
        scripts_text += ScriptsPagination.get_script_short_info(script, i)
        scripts_text += "\n"

    scripts_text += f"📄 Показано: {len(scripts_data['scripts'])} из {scripts_data['total']}"

    # Создаем клавиатуру
    total_pages = (scripts_data['total'] + scripts_data['per_page'] - 1) // scripts_data['per_page']
    keyboard = ScriptsPagination.create_pagination_keyboard(
        current_page=page,
        total_pages=total_pages,
        scripts_on_page=scripts_data['scripts']
    )

    await callback.message.edit_text(scripts_text, reply_markup=keyboard)
    await callback.answer()

# Обработчик детального просмотра скрипта
@user_history.callback_query(F.data.startswith("script_detail_"))
async def handle_script_detail(callback: types.CallbackQuery):
    """Обработка просмотра детальной информации о скрипте"""
    script_id = int(callback.data.split("_")[-1])

    # Получаем детальную информацию о скрипте
    script = await sync_to_async(get_script_by_id)(script_id)

    if not script:
        await callback.answer("❌ Скрипт не найден")
        return

    # Формируем детальную информацию
    status_emoji = ScriptsPagination.get_status_emoji(script)
    usage_percent = (script.get('used', 0) / script.get('max_usage', 1)) * 100

    detail_text = (
        f"📋 <b>Детали скрипта</b>\n\n"
        f"🆔 <b>ID:</b> {script.get('id')}\n"
        f"📝 <b>Название:</b> {script.get('script', 'Неизвестно')}\n"
        f"🔑 <b>Ключ:</b> <code>{script.get('key', 'Не задан')}</code>\n"
        f"📊 <b>Статус:</b> {status_emoji} {'Активен' if script.get('is_active') else 'Неактивен'}\n"
        f"🎯 <b>Тип:</b> {script.get('script_type', 'Неизвестно')}\n\n"
        f"📈 <b>Использование:</b>\n"
        f"   • Использовано: {script.get('used', 0)}/{script.get('max_usage', 0)} ({usage_percent:.1f}%)\n\n"
        f"⏰ <b>Время действия:</b>\n"
        f"   • Начало: {ScriptsPagination.format_datetime(script.get('start_at'))}\n"
        f"   • Окончание: {ScriptsPagination.format_datetime(script.get('stop_at'))}\n\n"
        f"🔐 <b>Безопасность:</b>\n"
        f"   • Отпечаток: {script.get('fingerprint', 'Не задан')}\n"
        f"   • Первая активация: {ScriptsPagination.format_datetime(script.get('first_activate'))}\n"
        f"   • Первое использование: {ScriptsPagination.format_datetime(script.get('first_seen'))}\n"
    )

    keyboard = ScriptsPagination.create_script_detail_keyboard(script_id, script.get('is_active', False))

    await callback.message.edit_text(detail_text, reply_markup=keyboard)
    await callback.answer()

# Обработчик активации скрипта
@user_history.callback_query(F.data.startswith("activate_script_"))
async def handle_activate_script(callback: types.CallbackQuery):
    """Обработка активации скрипта"""
    script_id = int(callback.data.split("_")[-1])
    user_id = callback.from_user.id

    # Активируем скрипт
    result = await sync_to_async(activate_script)(script_id, user_id)

    if result.get('success'):
        await callback.answer("✅ Скрипт успешно активирован!", show_alert=True)
        # Обновляем отображение
        await handle_script_detail(callback)
    else:
        error_msg = result.get('error', 'Неизвестная ошибка')
        await callback.answer(f"❌ Ошибка активации: {error_msg}", show_alert=True)

# Обработчик деактивации скрипта
@user_history.callback_query(F.data.startswith("deactivate_script_"))
async def handle_deactivate_script(callback: types.CallbackQuery):
    """Обработка деактивации скрипта"""
    script_id = int(callback.data.split("_")[-1])
    user_id = callback.from_user.id

    # Деактивируем скрипт
    result = await sync_to_async(deactivate_script)(script_id, user_id)

    if result.get('success'):
        await callback.answer("⏸️ Скрипт деактивирован", show_alert=True)
        # Обновляем отображение
        await handle_script_detail(callback)
    else:
        error_msg = result.get('error', 'Неизвестная ошибка')
        await callback.answer(f"❌ Ошибка деактивации: {error_msg}", show_alert=True)

# Обработчик копирования ключа
@user_history.callback_query(F.data.startswith("copy_key_"))
async def handle_copy_key(callback: types.CallbackQuery):
    """Обработка копирования ключа скрипта"""
    script_id = int(callback.data.split("_")[-1])

    script = await sync_to_async(get_script_by_id)(script_id)

    if not script:
        await callback.answer("❌ Скрипт не найден")
        return

    key = script.get('key', '')
    if key:
        await callback.answer(f"🔑 Ключ скопирован: {key}", show_alert=True)
    else:
        await callback.answer("❌ Ключ не найден", show_alert=True)

# Обработчик обновления статуса скрипта
@user_history.callback_query(F.data.startswith("refresh_script_"))
async def handle_refresh_script(callback: types.CallbackQuery):
    """Обработка обновления статуса скрипта"""
    script_id = int(callback.data.split("_")[-1])

    # Получаем обновленную информацию
    script = await sync_to_async(get_script_by_id)(script_id)

    if not script:
        await callback.answer("❌ Скрипт не найден")
        return

    # Обновляем отображение
    await handle_script_detail(callback)
    await callback.answer("🔄 Статус обновлен")

# Обработчик удаления скрипта
@user_history.callback_query(F.data.startswith("delete_script_"))
async def handle_delete_script(callback: types.CallbackQuery):
    """Обработка удаления скрипта"""
    script_id = int(callback.data.split("_")[-1])

    # Здесь должна быть логика удаления скрипта
    # Пока просто показываем предупреждение
    await callback.answer("⚠️ Функция удаления будет доступна позже", show_alert=True)

# Обработчик игнорирования нажатий на текущую страницу
@user_history.callback_query(F.data == "current_page")
async def handle_current_page(callback: types.CallbackQuery):
    """Обработка нажатия на индикатор текущей страницы"""
    await callback.answer("📄 Текущая страница")