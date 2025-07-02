from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def cancel_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='❌Отменить', callback_data='cancel')
            ]
        ]
    )

def select_time(redis_id):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='📅Выбрать время', web_app={"url": f"https://t.me/aihelper_bot?start={redis_id}"})
            ]
        ]
    )