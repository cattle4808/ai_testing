from aiogram import Router
from aiogram import F, types
from asgiref.sync import sync_to_async

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
    user_id = message.from_user.id

    referral_link = await sync_to_async(refferal.generate_referral_link)(user_id)
    referral_buys = await sync_to_async(operations.get_referrals_counts)(user_id)
    invited_users = await sync_to_async(operations.get_referrals_inviters)(user_id)

    reward_per_referral = 25_000
    max_discount = 125_000

    successful_referrals = len(referral_buys["all"])
    unused_referrals = len(referral_buys["unused"])
    total_discount = unused_referrals * reward_per_referral

    await message.answer(
        "<b>👥 Реферальная программа</b>\n\n"
        "💸 <b>За каждого человека</b>, который совершит покупку по вашей ссылке, вы получаете "
        f"<b>скидку {reward_per_referral:,} сум</b>.\n"
        f"🔐 <b>Максимальная скидка</b> на одну покупку — <b>{max_discount:,} сум</b>.\n\n"
        "📌 <b>Ваша реферальная ссылка:</b>\n"
        f"{referral_link}\n\n"
        "📊 <b>Статистика</b>:\n"
        f"— Приглашено: <b>{len(invited_users)} человек</b>\n"
        f"— Совершили покупку: <b>{successful_referrals} человек</b>\n"
        f"— Доступная скидка: <b>{unused_referrals} / {total_discount:,} сум</b>",
        parse_mode="HTML"
    )



@user.message(F.text == CommandMap.User.INSTRUCTION)
async def instruction(message: types.Message):
    await message.delete()
    await message.answer("Инструкция")

@user.message(F.text == CommandMap.User.SUPPORT)
async def support(message: types.Message):
    await message.delete()
    await message.answer(
        "<b>🛠 Служба поддержки</b>\n\n"
        "Мы ценим ваше доверие и всегда готовы помочь.\n"
        "Если у вас возникли сложности — обращайтесь напрямую. "
        "Мы ответим максимально быстро и с заботой о каждом пользователе.\n\n"
        "🔐 <b>Ваша безопасность</b> — наш главный приоритет.\n"
        "🎯 <b>Ваша уверенность</b> — наша ответственность.\n\n",
        parse_mode="HTML",
        reply_markup=user_inline.support()
    )


@user.message(F.text == CommandMap.User.MY_SCRIPTS)
async def my_shops(message: types.Message):
    await message.delete()


