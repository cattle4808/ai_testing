from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from bot import CommandMap

def main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=CommandMap.User.BUY_SCRIPT),
                KeyboardButton(text=CommandMap.User.MY_SCRIPTS),
            ],
            [
                KeyboardButton(text=CommandMap.User.MY_DATA),
                KeyboardButton(text=CommandMap.User.INSTRUCTION)
            ],
            [
                KeyboardButton(text=CommandMap.User.SUPPORT),
            ]
        ],
        resize_keyboard=True
    )

