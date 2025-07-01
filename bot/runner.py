from . import bot, dp

from . handlers import admin, main


dp.include_router(admin)
dp.include_router(main)

