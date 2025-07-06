from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from django.conf import settings

bot = Bot(token=settings.BOT_TOKEN)
storage = RedisStorage.from_url(settings.REDIS_URL)

dp = Dispatcher(storage=storage)



class CommandMap:
    class User:
        BUY_SCRIPT = "💰Купить решение"
        MY_SCRIPTS = "📦 Покупки"
        MY_DATA = "👥 Рефералы"
        INSTRUCTION = "📄 Инструкции"
        SUPPORT = "🛠 Поддержка"


    class Admin:
        DEV_MENU = "Dev_menu"

