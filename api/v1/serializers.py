from rest_framework import serializers
from datetime import datetime
from pytz import timezone

from . import models


def parse_tashkent_datetime(dt_str: str):
    tz = timezone('Asia/Tashkent')
    naive = datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
    aware = tz.localize(naive)
    return aware

class CreateScriptSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.IdScript
        fields = '__all__'

class TgUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.TgUsers
        fields = '__all__'

class GetMyScriptsSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.IdScript
        fields = [
            'script', 'key', 'start_at', 'stop_at',
            'is_active', 'used', 'max_usage',
            'first_activate', 'first_seen'
        ]

class ChangeScriptISActiveSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.IdScript
        fields = [
            'script', 'key', 'start_at', 'stop_at',
            'is_active', 'used', 'max_usage',
            'first_activate', 'first_seen'
        ]
        read_only_fields = [
            'script', 'key', 'start_at', 'stop_at',
            'used', 'max_usage', 'first_activate', 'first_seen'
        ]


class ChangeScriptTimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.IdScript
        fields = [
            'script', 'key', 'start_at', 'stop_at',
            'is_active', 'used', 'max_usage',
            'first_activate', 'first_seen'
        ]
        read_only_fields = [
            'script', 'is_active', 'stop_at'
            'used', 'max_usage', 'first_activate', 'first_seen'
        ]


class AiAnswerSerializer(serializers.ModelSerializer):
    fingerprint = serializers.CharField(required=False, allow_blank=True, write_only=True)
    script_instance = serializers.PrimaryKeyRelatedField(
        source='script',
        queryset=models.IdScript.objects.all(),
        write_only=True
    )

    class Meta:
        model = models.Answer
        fields = ['script', 'script_instance', 'image', 'answer', 'created_at', 'fingerprint']
        read_only_fields = ['created_at', 'answer']
