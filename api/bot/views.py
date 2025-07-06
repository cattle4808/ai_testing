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
        payload = json.loads(request.body)

        date_str = payload["date"]
        time_str = payload["time"]
        tg_id = payload["user_id"]
        init_data = payload["initData"]
        username = payload.get("username")

        check_init_data = TgCrypto().verify_init_data(init_data)
        if not check_init_data:
            raise Http404()

        try:
            start_at_naive = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
            start_at = make_aware(start_at_naive)
        except ValueError:
            return Response({"error": "Неверный формат даты или времени"}, status=400)

        script = operations.create_script(user_id=tg_id, start_at=start_at)

        print(script)
        bot.send_message(chat_id=tg_id, text=str(script))

        return Response(script)

def select_time(request):
    return render(request, 'time_select/create_script.html')