from aiogram import Router
from aiogram import F, types
from asgiref.sync import sync_to_async
from setuptools.command.build_py import make_writable

from bot.keyboards.user import inline as user_inline, reply as user_reply
from bot.keyboards.admin import inline as admin_inline, reply as admin_reply
from bot import CommandMap

from services.models import operations
from services.models import refferal

user = Router()

@user.message(F.text == CommandMap.User.BUY_SCRIPT)
async def buy_script(message: types.Message):
    await message.answer("Купить скрипт", reply_markup=user_inline.select_time())

@user.message(F.text == CommandMap.User.MY_DATA)
async def my_referrals(message: types.Message):
    await message.delete()
    await message.answer("Рефералы")

    user_id = message.from_user.id

    referral_link = await sync_to_async(refferal.generate_referral_link)(user_id)
    await message.answer(referral_link)

    refferal_buys = await sync_to_async(operations.get_referrals_counts)(user_id)
    inviter_users = await sync_to_async(operations.get_referrals_inviters)(user_id)

    await message.answer(f"Юзеры с рефералки: {len(inviter_users)}\n\n"
                         f"Покупок с вашей рефералки: {len(refferal_buys['all'])}\n\n"
                         f"Подробнее покупки: {refferal_buys}"
                         )

@user.message(F.text == CommandMap.User.INSTRUCTION)
async def instruction(message: types.Message):
    await message.delete()
    await message.answer("Инструкция")

@user.message(F.text == CommandMap.User.SUPPORT)
async def support(message: types.Message):
    await message.delete()
    await message.answer("Поддержка")

@user.message(F.text == CommandMap.User.MY_SCRIPTS)
async def my_shops(message: types.Message):
    await message.delete()


