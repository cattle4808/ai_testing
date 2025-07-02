from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from aiogram import types

from bot import bot, dp


@csrf_exempt
async def webhook(request):
    if request.method != "POST":
        return JsonResponse({"error": "only POST allowed"}, status=405)
    body = request.body.decode()
    update = types.Update.model_validate_json(body)
    await dp.feed_webhook_update(bot, update)
    return JsonResponse({"ok": True})