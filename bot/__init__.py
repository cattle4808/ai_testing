from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from django.conf import settings

bot = Bot(token=settings.BOT_TOKEN)
storage = RedisStorage.from_url(settings.REDIS_URL)

dp = Dispatcher(storage=storage)



class CommandMap:
    class User:
        BUY_SCRIPT = "Купить скрипт"
        MY_SCRIPTS = "Мои скрипты"
        MY_DATA = "Мои данные"
        INSTRUCTION = "Инструкции"
        SUPPORT = "Поддержка"


    class Admin:
        DEV_MENU = "Dev_menu"

