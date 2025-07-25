from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from django.conf import settings

def cancel_keyboard(redis_key):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='❌Отменить', callback_data=f'cancel_payment:{redis_key}')
            ]
        ]
    )

def select_time():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='📅Выбрать время', web_app={"url": settings.WEB_APP_SELECT_TIME_URL})
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

def send_or_receive_payment(redis_key) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📤 Отправить на проверку",
                    callback_data=f"send_pay:{redis_key}",
                )
            ],
            [
                InlineKeyboardButton(
                    text="📥 заново отправить чек",
                    callback_data=f"resend_pay:{redis_key}",
                )
            ],
            [
                InlineKeyboardButton(text='❌Отменить', callback_data=f'cancel_payment:{redis_key}')
            ]
        ]
    )

def change_buy(redis_key):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Оплатить",
                    callback_data=f"buy_script:{redis_key}"
                )
            ]
        ]
    )

def police_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Принять политику",
                    callback_data="accept_policy"
                )
            ]
        ]
    )
