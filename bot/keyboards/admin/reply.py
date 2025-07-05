from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from bot import CommandMap

def main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=CommandMap.Admin.DEV_MENU),
            ]
        ],
        resize_keyboard=True
    )