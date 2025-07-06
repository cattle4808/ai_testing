from . import bot, dp

from . handlers import admin, main, user, user_callback


dp.include_router(admin)
dp.include_router(main)
dp.include_router(user)
dp.include_router(user_callback)
