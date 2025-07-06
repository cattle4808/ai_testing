import json
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import Http404
from aiogram import types
from idna.idnadata import scripts
from rest_framework import views

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

class CreateScriptView(views.APIView):
    def post(self, request, *args, **kwargs):
        try:
            payload = json.loads(request.body)
            start_str = payload["start"]
            tg_id = payload["user_id"]
            username = payload.get("username", None)
            init_data = payload["initData"]
        except (ValueError, KeyError):
            raise Http404()

        check_init_data = TgCrypto().verify_init_data(init_data)
        if not check_init_data:
            raise Http404()

        script = operations.create_script(user_id=tg_id, start_at=start_str)

        print(script)

        bot.send_message(chat_id=tg_id, text=str(script))


def select_time(request):
    return render(request, 'time_select/create_script.html')