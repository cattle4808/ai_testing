from aiogram.filters import BaseFilter
from aiogram.types import Message
from asgiref.sync import sync_to_async

from services.models import operations

class HasAcceptedPolicy(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        user = await sync_to_async(operations.get_or_create_tg_user)(user_id=message.from_user.id)
        return user.get("police", False)