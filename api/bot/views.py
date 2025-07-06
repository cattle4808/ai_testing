import json
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import Http404
from aiogram import types
from idna.idnadata import scripts
from rest_framework import views
from rest_framework.response import Response


from services.crypto import SimpleCipher, TgCrypto
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

from datetime import datetime, timedelta
from django.utils.timezone import make_aware

class CreateScriptView(views.APIView):
    def post(self, request, *args, **kwargs):
        try:
            payload = json.loads(request.body.decode("utf-8"))
        except json.JSONDecodeError:
            return Response({"error": "Невалидный JSON"}, status=400)

        # Получаем поля с .get() и проверкой на наличие
        start_str = payload.get("start")
        end_str = payload.get("end")
        qid = payload.get("qid")
        tg_id = payload.get("user_id")
        init_data = payload.get("initData")
        username = payload.get("username", None)  # Необязательное поле

        # Проверка обязательных полей
        required_fields = [start_str, end_str, qid, tg_id, init_data]
        if not all(required_fields):
            return Response({"error": "Отсутствуют обязательные поля"}, status=400)

        # 👉 Логика твоего скрипта здесь
        try:
            result = operations.create_script(
                user_id=tg_id,
                start_at=start_str,
                stop_at=end_str
            )
            return Response(result, status=200)

        except Exception as e:
            # можно логировать: logger.exception("Ошибка при создании скрипта")
            return Response({"error": "ERR_CREATE_SCRIPT"}, status=500)

def select_time(request):
    return render(request, 'time_select/create_script.html')