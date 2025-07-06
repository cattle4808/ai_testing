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

class CreateScriptView(views.APIView):
    def post(self, request, *args, **kwargs):
        try:
            payload = json.loads(request.body)
            start_str = payload["start"]
            tg_id = payload["user_id"]
            init_data = payload["initData"]

            if not TgCrypto().verify_init_data(init_data):
                raise Http404()

            try:
                start_at = datetime.fromisoformat(start_str)
            except ValueError:
                return Response({"error": "Invalid datetime format"}, status=400)

            script = operations.create_script(user_id=tg_id, start_at=start_at)

            bot.send_message(chat_id=tg_id, text=str(script))

            return Response(script, status=status.HTTP_201_CREATED)

        except (KeyError, json.JSONDecodeError):
            raise Http404()


def select_time(request):
    return render(request, 'time_select/create_script.html')