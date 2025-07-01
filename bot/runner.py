from . import bot, dp

from . handlers import admin, main

main.setup_handlers(dp)
admin.setup_handlers(dp)

