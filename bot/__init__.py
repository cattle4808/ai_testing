from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from django.conf import settings

bot = Bot(token=settings.BOT_TOKEN)
dp = Dispatcher(bot)

storage = RedisStorage.from_url(settings.REDIS_URL)

def setup():
    from . import handlers
    dp.include_router(handlers.setup_handlers(dp))

