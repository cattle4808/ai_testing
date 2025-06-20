import base64

from rest_framework import views
from rest_framework import status
from django.http import Http404, HttpResponse
from django.views import View


from core.settings import DOMAIN
from . import mixins
from . import serializers
from . import models
from .scripts import BASE_SCRIPT_PROD_UUID
from . ai_service import base64_image_answer_question
from . import permissions
from . service import model2, model4, model6

class GenerateScriptView(mixins.SuccessErrorResponseMixin, views.APIView):
    permission_classes = [permissions.TokenPermission]
    def post(self, request):
        serializer = serializers.GenerateNoJsScriptSerializer(data=request.data)
        if not serializer.is_valid():
            return self.error("validation_error", "Validation error", serializer.errors)
        instance = serializer.save()
        return self.success(serializers.GetNoJsScriptInfoSerializer(instance).data)

class GetKeyNoJsScriptInfoView(mixins.SuccessErrorResponseMixin, views.APIView):
    def get(self, request, key):
        try:
            instance = models.NoJsIdScript.objects.get(key=key)
            return self.success(serializers.GetNoJsScriptInfoSerializer(instance).data)
        except models.NoJsIdScript.DoesNotExist:
            return self.error("script_not_found", "Script not found", status_code=status.HTTP_404_NOT_FOUND)

class ChangeNoJsActivateView(mixins.SuccessErrorResponseMixin, views.APIView):
    permission_classes = [permissions.TokenPermission]

    def post(self, request):
        serializer = serializers.ChangeNoJsScriptActivateSerializer(data=request.data)
        if not serializer.is_valid():
            return self.error("validation_error", "Invalid data", serializer.errors)
        try:
            instance = models.NoJsIdScript.objects.get(key=serializer.validated_data["key"])
            instance.is_active = serializer.validated_data["is_active"]
            instance.save(update_fields=["is_active"])
            return self.success(serializers.GetNoJsScriptInfoSerializer(instance).data)
        except models.NoJsIdScript.DoesNotExist:
            return self.error("script_not_found", "Script not found", status_code=status.HTTP_404_NOT_FOUND)


class GetNoJsScriptView(View):
    def script_filter(self, script_type, key):
        template = {
            'base': BASE_SCRIPT,
            'test': TEST_SCRIPT,
            'base_prod': BASE_SCRIPT_PROD,
            'base_prof_uuid': BASE_SCRIPT_PROD_fp_to_uuid
        }.get(script_type, BASE_SCRIPT_PROD_fp_to_uuid)

        return template.format(key=key, domain=DOMAIN)

    def get(self, request, script):
        if not script:
            raise Http404()
        try:
            script_info = models.NoJsIdScript.objects.get(script=script)
            if not script_info.is_access_time_valid():
                raise Http404()

            content = self.script_filter(script_info.script_type, script_info.key)
            return HttpResponse(content, content_type='application/javascript')

        except models.NoJsIdScript.DoesNotExist:
            raise Http404()
        except Exception:
            raise Http404()

class ScriptCheckView(mixins.SuccessErrorResponseMixin, views.APIView):

    def get_image_base64(self, image_file):
        image_file.seek(0)
        encoded = base64.b64encode(image_file.read()).decode("utf-8")
        image_file.seek(0)
        return encoded

    def post(self, request):
        serializer = serializers.IdScriptCheckSerializer(data=request.data)
        if not serializer.is_valid():
            return self.error("validation_error", "Validation error", serializer.errors)

        script = serializer.validated_data['script_instance']
        image = serializer.validated_data['image']

        base64_img = self.get_image_base64(image)
        # data = base64_image_answer_question(base64_img)
        data = model4.base64_image_answer_question(base64_img)

        if not data or not data.get("answer"):
            return self.error("ai_parse_error", "Answer not found", status_code=500)

        models.NoJsAnswer.objects.create(script=script, image=image, answer=data)
        script.increment_usage()

        return self.success(data)