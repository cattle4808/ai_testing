import json

from . main import main
from . admin import admin
from . user import user
from . states import state_user
from . callback import user_callback, admin_callback

from .. import dp, redis


def set_router():
    dp.include_router(main)
    dp.include_router(admin)
    dp.include_router(user)
    dp.include_router(state_user)
    dp.include_router(user_callback)
    dp.include_router(admin_callback)

__all__ = ['main', 'admin', 'user', 'user_callback', 'state_user']

async def get_redist_data(redis_id_key: str) -> dict:
    raw_data = await redis.get(redis_id_key)
    if not raw_data:
        return {}
    data = json.loads(raw_data)
    return data
