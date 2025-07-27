import pprint

from aiogram import Router
from aiogram import F, types
from asgiref.sync import sync_to_async
from django.conf import settings
from aiogram.fsm.context import FSMContext


from ..keyboards.user import inline as user_inline, reply as user_reply
from ..keyboards.admin import inline as admin_inline, reply as admin_reply
from .. import CommandMap
from ..fsm.user import UserPaymentCheck
from ..filters import police
from .. import bot

from services.models import operations
from services.models import refferal


user = Router()

@user.message(F.text == CommandMap.User.BUY_SCRIPT, police.HasAcceptedPolicy())
async def buy_script(message: types.Message, state: FSMContext):
    state_name = await state.get_state()
    if state_name == UserPaymentCheck.waiting_for_img:
        try:
            await message.delete()
        except:
            pass

        redis_data = await state.get_data()
        redis_key = redis_data.get("redis_key")

        await message.answer(
            "⛔ Сначала завершите текущую оплату — отправьте фото чека.\n"
            f"Или отмените оплату",
            reply_markup=user_inline.cancel_keyboard(redis_key)
        )
        return

    await message.answer(
        "<b>💼 Покупка решения — быстро и надёжно</b>\n\n"
        "<b>1️⃣ Выберите дату и время теста</b>\n"
        "Укажите заранее, чтобы мы всё подготовили.\n\n"
        "<b>2️⃣ Оплатите заказ</b>\n"
        "Мы принимаем оплату и сразу начинаем работу.\n\n"
        "<b>3️⃣ Получите решение через AFT</b>\n"
        "Точно в нужное время, без задержек.\n\n"
        "<b>🔐 Мы гарантируем:</b>\n"
        "– Полную конфиденциальность\n"
        "– Своевременную отправку\n"
        "– Рабочее и проверенное решение",
        reply_markup=user_inline.select_time(),
        parse_mode="HTML"
    )


@user.message(F.text == CommandMap.User.MY_DATA)
async def my_referrals(message: types.Message, state: FSMContext):
    state_name = await state.get_state()
    if state_name == UserPaymentCheck.waiting_for_img:
        try:
            await message.delete()
        except:
            pass

        redis_data = await state.get_data()
        redis_key = redis_data.get("redis_key")

        await message.answer(
            "⛔ Сначала завершите текущую оплату — отправьте фото чека.\n"
            f"Или отмените оплату",
            reply_markup=user_inline.cancel_keyboard(redis_key)
        )
        return

    user_id = message.from_user.id

    referral_link = await sync_to_async(refferal.generate_referral_link)(user_id)
    referral_buys = await sync_to_async(operations.get_referrals_counts)(user_id)
    invited_users = await sync_to_async(operations.get_referrals_inviters)(user_id)

    reward_per_referral = settings.REWERD_PER_REFFERAL
    max_discount = settings.MAX_DISCOUNT

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



@user.message(F.text == CommandMap.User.INSTRUCTION, police.HasAcceptedPolicy())
async def instruction(message: types.Message, state: FSMContext):
    state_name = await state.get_state()
    if state_name == UserPaymentCheck.waiting_for_img:
        try:
            await message.delete()
        except:
            pass

        redis_data = await state.get_data()
        redis_key = redis_data.get("redis_key")

        await message.answer(
            "⛔ Сначала завершите текущую оплату — отправьте фото чека.\n"
            f"Или отмените оплату",
            reply_markup=user_inline.cancel_keyboard(redis_key)
        )
        return

    common_instruction = (
        f"📌 <b>Инструкция по запуску скрипта</b>\n\n"
        f"🔹 <b>Что это?</b>\n"
        f"Ты получил персональную ссылку, которая позволяет активировать вспомогательный интерфейс прямо в браузере:\n"
        f"<code>javascript:import('//aft.lol/&lt;твой_код&gt;')</code>\n\n"

        f"🔧 <b>Как использовать:</b>\n"
        f"1. Открой любой веб-сайт, с которым ты сейчас работаешь\n"
        f"2. Убедись, что страница полностью загрузилась\n"
        f"3. Скопируй выданную ссылку и вставь её в адресную строку браузера (не в поисковик!)\n"
        f"4. Нажми Enter — система активирует необходимый функционал\n\n"

        f"⚙️ <b>Требования:</b>\n"
        f"• Современный браузер (Chrome, Firefox, Edge на ПК)\n"
        f"• Скрипт не работает на мобильных устройствах и в Safari\n"

        f"❓ <b>Если возникли вопросы:</b>\n"
        f"• Проверь, что вставляешь ссылку без пробелов и лишних символов\n"
        f"• Обнови страницу и попробуй ещё раз\n\n"

        f"📬 <b>Поддержка:</b> <a href='https://t.me/AFT_Admin1'>@AFT_Admin1</a>\n\n"
        f"<i>Инструкция предоставлена для активации вспомогательного интерфейсного решения.</i>"
    )

    try:
        await bot.send_video(
            chat_id=message.from_user.id,
            video='BAACAgIAAxkBAAIYMmiFwK52pClYD7QkOjurR1mf6bz4AAIzcAACQmcxSFDvFQgTHYzFNgQ',
            caption=common_instruction,
            parse_mode="HTML"
        )
    except Exception as e:
        print(e)


@user.message(F.text == CommandMap.User.SUPPORT, police.HasAcceptedPolicy())
async def support(message: types.Message, state: FSMContext):
    state_name = await state.get_state()
    if state_name == UserPaymentCheck.waiting_for_img:
        try:
            await message.delete()
        except:
            pass

        redis_data = await state.get_data()
        redis_key = redis_data.get("redis_key")

        await message.answer(
            "⛔ Сначала завершите текущую оплату — отправьте фото чека.\n"
            f"Или отмените оплату",
            reply_markup=user_inline.cancel_keyboard(redis_key)
        )
        return

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


# @user.message(F.text == CommandMap.User.MY_SCRIPTS)
# async def my_shops(message: types.Message, state: FSMContext):
#     state_name = await state.get_state()
#     if state_name == UserPaymentCheck.waiting_for_img:
#         try:
#             await message.delete()
#         except:
#             pass
#
#         redis_data = await state.get_data()
#         redis_key = redis_data.get("redis_key")
#
#         await message.answer(
#             "⛔ Сначала завершите текущую оплату — отправьте фото чека.\n"
#             f"Или отмените оплату",
#             reply_markup=user_inline.cancel_keyboard(redis_key)
#         )
#         return
#
#     user_id = message.from_user.id
#
#     await message.answer(
#         "<b>📂 Мои скрипты</b>\n\n"
#         "Здесь вы можете управлять своими скриптами.\n"
#     )
#
#     my_scripts = await sync_to_async(operations.get_my_scripts)(user_id)
#
#     pprint.pprint(my_scripts, indent=4)


