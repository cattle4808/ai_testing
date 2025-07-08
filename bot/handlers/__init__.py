from . main import main
from . admin import admin
from . user import user
from . states import state_user
from . callback import user_callback

from .. import dp


def set_router():
    dp.include_router(main)
    dp.include_router(admin)
    dp.include_router(user)
    dp.include_router(state_user)
    dp.include_router(user_callback)

__all__ = ['main', 'admin', 'user', 'user_callback', 'state_user']