from django.http import HttpResponse
from rest_framework import views

from . import models
from . import api_v1_models


class WebhookView(views.APIView):
    def post(self, request, *args, **kwargs):
        return HttpResponse(status=200)

    def get(self, request, *args, **kwargs):
        return HttpResponse(status=200)


