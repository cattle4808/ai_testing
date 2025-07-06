import json
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import Http404
from aiogram import types
from idna.idnadata import scripts
from rest_framework import views, status
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
            payload = json.loads(request.body)
            start_str = payload.get("start")
            end_str   = payload.get("end")
            qid       = payload.get("qid")
            tg_id     = payload.get("user_id")
            username  = payload.get("username")
            init_data = payload.get("initData")

            if not (start_str and end_str and tg_id):
                return Response({"error": "Некорректные или неполные данные"}, status=status.HTTP_400_BAD_REQUEST)

            start_at = make_aware(datetime.strptime(start_str, "%d.%m.%Y %H:%M"))
            stop_at  = make_aware(datetime.strptime(end_str, "%d.%m.%Y %H:%M"))

            chech_init_data = TgCrypto().verify_init_data(init_data)

            print("chech_init_data:", chech_init_data)


            print(f"Создан скрипт: start={start_at}, stop={stop_at}, user_id={tg_id}, username={username}, qid={qid}")


        except Exception as e:
            print(f"[ERR_CREATE_SCRIPT] Exception: {e}")
            return Response({"error": "ERR_CREATE_SCRIPT"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def select_time(request):
    return render(request, 'time_select/create_script.html')