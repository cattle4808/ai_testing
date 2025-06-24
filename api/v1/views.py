import base64

from rest_framework import views, generics, status
from rest_framework.generics import UpdateAPIView
from rest_framework.response import Response
from django.utils.dateparse import parse_datetime
from datetime import timedelta

from serices.image2answer.model1_openai import base64_image_answer_question
from . import models, serializers, mixins


class CreateIdScriptApiView(mixins.SuccessErrorResponseMixin, generics.ListCreateAPIView):
    queryset = models.IdScript.objects.all()
    serializer_class = serializers.CreateScriptSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return self.success(serializer.data)

class GetOrCreateTgUserView(mixins.SuccessErrorResponseMixin, views.APIView):
    def post(self, request, *args, **kwargs):
        instance, created = models.TgUsers.objects.get_or_create(defaults=request.data)
        serializer = serializers.TgUserSerializer(instance)
        return self.success(serializer.data, status_code=201 if created else 200)

    def get(self, request, *args, **kwargs):
        users = models.TgUsers.objects.all()
        serializer = serializers.TgUserSerializer(users, many=True)
        return self.success(serializer.data)


class GetMyScriptsView(mixins.SuccessErrorResponseMixin, generics.ListAPIView):
    serializer_class = serializers.GetMyScriptsSerializer

    def get_queryset(self):
        return models.IdScript.objects.filter(owner__user=self.request.query_params.get('user'))

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return self.success(serializer.data)


class ChangeIsActivateView(mixins.SuccessErrorResponseMixin, generics.UpdateAPIView):
    queryset = models.IdScript.objects.all()
    serializer_class = serializers.ChangeScriptISActiveSerializer
    lookup_field = 'key'

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        return self.success(response.data)


class ChangeScriptTimeView(mixins.SuccessErrorResponseMixin, views.APIView):
    def put(self, request, *args, **kwargs):
        key = request.data.get("key")
        start_at_str = request.data.get("start_at")

        if not key:
            return self.error(
                code=3001,
                message="key not passed",
                details={"field": "key"},
                status_code=400
            )

        if not start_at_str:
            return self.error(
                code=2001,
                message="start_at not passed",
                details={"field": "start_at"},
                status_code=400
            )

        start_at = parse_datetime(start_at_str)
        if not start_at:
            return self.error(
                code=2002,
                message="start_at is not valid datetime format",
                details={"value": start_at_str},
                status_code=400
            )

        try:
            script = models.IdScript.objects.get(key=key)
        except models.IdScript.DoesNotExist:
            return self.error(
                code=3000,
                message="Script not found",
                details={"key": key},
                status_code=404
            )

        script.start_at = start_at
        script.stop_at = start_at + timedelta(hours=2)
        script.save()

        serializer = serializers.ChangeScriptISActiveSerializer(script)
        return self.success(data=serializer.data)


class AiAnswerCheckView(mixins.SuccessErrorResponseMixin, generics.ListCreateAPIView):
    def get_image_base64(self, image_file):
        image_file.seek(0)
        encoded = base64.b64encode(image_file.read()).decode("utf-8")
        image_file.seek(0)
        return encoded

    def post(self, request, *args, **kwargs):
        serializer = serializers.AiAnswerSerializer(data=request.data)

        if not serializer.is_valid():
            return self.error("validation_error", "Validation error", serializer.errors)

        script = serializer.validated_data['script_instance']
        image = serializer.validated_data['image']

        base64_img = self.get_image_base64(image)

        data = base64_image_answer_question(base64_img)

        if not data or not data.get("answer"):
            return self.error("ai_parse_error", "Answer not found", status_code=500)

        if serializer.is_valid():
            serializer.save()
            return self.success(data=serializer.data, status_code=201)

        return self.error(
            code=1001,
            message="Validation error",
            details=serializer.errors,
            status_code=400
        )

