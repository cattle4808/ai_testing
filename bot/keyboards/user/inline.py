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

def support():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📚 Популярные вопросы", callback_data="faq")
            ],
            [
                InlineKeyboardButton(text="📩 Написать администратору", url="https://t.me/AFT_Admin1")
            ]
        ]
    )

def back_support():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🔙 Назад", callback_data=f"back_to_support")
            ]
        ]
    )

def send_or_receive_payment(key) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📤 Отправить на проверку",
                    callback_data=f"send:{key}",
                )
            ],
            [
                InlineKeyboardButton(
                    text="📥 заново отправить чек",
                    callback_data=f"pay:{key}",
                )
            ]
        ]
    )

def change_buy(key):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Оплатить",
                    callback_data=f"buy:{key}"
                )
            ]
        ]
    )