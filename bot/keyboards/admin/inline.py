from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def check_payment(redis_key):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Подтвердить", callback_data=f"allow_payment_from_admin:{redis_key}"),
                InlineKeyboardButton(text="Отклонить:", callback_data=f"deny_payment_from_admin:{redis_key}")
            ]
        ]
    )