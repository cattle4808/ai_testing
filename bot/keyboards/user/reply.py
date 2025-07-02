from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text='Купить AI-помощник'),
                KeyboardButton(text='Мои скрипты'),
            ],
            [
                KeyboardButton(text='Инструкция'),
                KeyboardButton(text='Поддержка'),
            ]
        ],
        resize_keyboard=True
    )

