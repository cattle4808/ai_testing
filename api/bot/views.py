from django.http import HttpResponse
from rest_framework import views

from . import models
from . import api_v1_models


from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from aiogram import types
# from bot import dp, bot

import asyncio

@method_decorator(csrf_exempt, name='dispatch')
class TelegramWebhookView(APIView):
    def post(self, request, *args, **kwargs):
        return HttpResponse(status=200)

    # def post(self, request, *args, **kwargs):
    #     update = types.Update(**request.data)
    #     loop = asyncio.new_event_loop()
    #     asyncio.set_event_loop(loop)
    #     loop.run_until_complete(dp.process_update(update))
    #     return HttpResponse()
