from aiogram.filters.state import State, StatesGroup


class UserPaymentCheck(StatesGroup):
    waiting_for_img = State()
    redis_key = State()
