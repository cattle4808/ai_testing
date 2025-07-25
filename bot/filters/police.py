from aiogram.filters import BaseFilter
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from asgiref.sync import sync_to_async

from .. import bot
from ..keyboards.user import inline

from services.models import operations

class HasAcceptedPolicy(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        user = await sync_to_async(operations.get_or_create_tg_user)(user_id=message.from_user.id)

        if not user.get("police", False):
            try:
                await message.delete()
            except Exception:
                pass

            await bot.send_document(
                chat_id=message.from_user.id,
                document="BQACAgIAAxkBAAIW_2iDiRrkxq2C4XoGwk2tHwZecaoQAAJndwACx90YSJrHnFqsl8QMNgQ",
                caption="<b>🛡️ Прежде чем начать, пожалуйста, ознакомьтесь и примите политику использования.</b>\n\n"
                        "Нажмите кнопку ниже, чтобы подтвердить согласие.",
                parse_mode="HTML",
                reply_markup=inline.police_kb()
            )
            return False
        return True