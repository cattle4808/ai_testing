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

from services.models import operations
from services.models import refferal

user_history = Router()


@user_history.message(F.text == CommandMap.User.MY_SCRIPTS)
async def my_shops(message: types.Message, state: FSMContext):
    state_name = await state.get_state()
    if state_name == UserPaymentCheck.waiting_for_img:
        try:
            await message.delete()
        except:
            pass
        await message.answer("⛔ Сначала завершите текущую оплату — отправьте фото чека.")
        return

    user_id = message.from_user.id

    await message.answer(
        "<b>📂 Мои скрипты</b>\n\n"
        "Здесь вы можете управлять своими скриптами.\n"
    )

    my_scripts = await sync_to_async(operations.get_my_scripts)(user_id)

    pprint.pprint(my_scripts, indent=4)
