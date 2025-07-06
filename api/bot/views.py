import json
import traceback

from asgiref.sync import async_to_sync, sync_to_async
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import Http404
from aiogram import types
from rest_framework import views, status
from rest_framework.response import Response
from datetime import datetime, timedelta
from django.utils.timezone import make_aware
import asyncio

from services.crypto import TelegramWebAppValidator
from services.models import operations
from bot.runner import bot, dp


@csrf_exempt
async def webhook(request):
    if request.method != "POST":
        raise Http404()
    body = request.body.decode()
    update = types.Update.model_validate_json(body)
    await dp.feed_webhook_update(bot, update)
    return JsonResponse({"ok": True})


@csrf_exempt
async def create_script_view(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=405)
    try:
        payload = json.loads(request.body)
        start_str = payload.get("start")
        end_str = payload.get("end")
        tg_user_id = payload.get("user_id")
        init_data = payload.get("initData")

        if not (start_str and end_str and tg_user_id):
            raise Http404()

        start_at = make_aware(datetime.strptime(start_str, "%d.%m.%Y %H:%M"))
        stop_at = make_aware(datetime.strptime(end_str, "%d.%m.%Y %H:%M"))

        if not TelegramWebAppValidator.is_safe(settings.BOT_TOKEN, init_data):
            raise Http404()

        user = await sync_to_async(operations.get_or_create_tg_user)(tg_user_id)
        referred_by = user.get("referred_by")
        print(user)

        script = await sync_to_async(operations.create_script)(tg_user_id, start_at)

        await bot.send_message(
            chat_id=tg_user_id,
            text=(
                f"Script: {script.get('script')}\n"
                f"Key: {script.get('key')}\n"
                f"Started at: {script.get('start_at')}\n"
                f"Stop at: {script.get('stop_at')}\n"
                f"Is active/buy: {script.get('is_active')}\n"
                f"Used: {script.get('max_usage')}/{script.get('used')}\n"
                f"Owner id: {script.get('max_usage')}"
            )
        )

        if referred_by:
            await sync_to_async(operations.add_to_referral)(tg_user_id, referred_by)

        return JsonResponse({"err": False})

    except Exception as e:
        print(f"[ERR_CREATE_SCRIPT] Exception: {e}")
        traceback.print_exc()
        return JsonResponse({"error": "ERR_CREATE_SCRIPT"}, status=500)


def select_time(request):
    return render(request, 'time_select/create_script.html')