from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def cancel_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='❌Отменить', callback_data='cancel')
            ]
        ]
    )

def select_time():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='📅Выбрать время', web_app={"url": "https://jjks.site/api/bot/select_time/"})
            ]
        ]
    )
