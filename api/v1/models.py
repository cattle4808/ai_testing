import secrets
import re
import string
from pathlib import Path
from django.db import models, transaction
from django.utils.timezone import now
from django.core.exceptions import ValidationError
from django.conf import settings
from datetime import timedelta
from itertools import product
import random


def generate_key(length=28):
    return secrets.token_urlsafe(length)[:length]

def generate_unique_script_name():
    alphabet = string.ascii_lowercase
    base_length = 3
    max_attempts = 100
    attempts = 0

    while attempts < max_attempts:
        name = ''.join(random.choices(alphabet, k=base_length))
        if not IdScript.objects.filter(script=name).exists():
            return name
        attempts += 1

    base_name = ''.join(random.choices(alphabet, k=base_length))
    suffix = 1
    while True:
        name = f"{base_name}{suffix}"
        if not IdScript.objects.filter(script=name).exists():
            return name
        suffix += 1

def validate_script_name(value):
    if not re.match(r'^[a-zA-Z0-9_\-]+$', value):
        raise ValidationError("Поле 'script' может содержать только латинские буквы, цифры, дефис и подчёркивание.")


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class IdScript(BaseModel):
    class ScriptChoices(models.TextChoices):
        BASE_PROF_UUID = 'base_prof_uuid', 'Base production script with UUID'

    script = models.CharField(
        max_length=100,
        unique=True,
        validators=[validate_script_name],
        help_text="Имя JS-файла (короткое и человекочитаемое)",
        blank=True,
        db_index=True
    )
    key = models.CharField(
        max_length=28,
        unique=True,
        blank=True,
        db_index=True
    )
    script_type = models.CharField(
        max_length=100,
        choices=ScriptChoices.choices,
        default=ScriptChoices.BASE_PROF_UUID
    )
    fingerprint = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        db_index=True
    )

    start_at = models.DateTimeField(db_index=True)
    stop_at = models.DateTimeField(db_index=True)
    is_active = models.BooleanField(default=False, db_index=True)
    used = models.IntegerField(default=0)
    max_usage = models.IntegerField(default=75)
    first_seen = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['is_active', 'start_at', 'stop_at']),
            models.Index(fields=['fingerprint', 'is_active']),
        ]

    def __str__(self):
        return self.script

    def is_access_time_valid(self) -> bool:
        now_ = now()
        return self.is_active and self.start_at <= now_ <= self.stop_at

    def check_fingerprint(self, fp: str) -> bool:
        return self.fingerprint == fp

    def assign_fingerprint_if_empty(self, fp: str) -> bool:
        if not self.fingerprint:
            updated = IdScript.objects.filter(
                id=self.id,
                fingerprint__isnull=True
            ).update(fingerprint=fp)

            if updated:
                self.fingerprint = fp
                return True
        return False

    def is_access_allowed(self, fp: str) -> bool:
        current_time = now()

        if not self.is_access_time_valid():
            return False

        if self.used >= self.max_usage:
            return False

        if not self.first_seen:
            IdScript.objects.filter(
                id=self.id,
                first_seen__isnull=True
            ).update(first_seen=current_time)
            self.first_seen = current_time

        if self.fingerprint:
            return self.fingerprint == fp

        if current_time - self.first_seen >= timedelta(seconds=20):
            return self.assign_fingerprint_if_empty(fp)
        return True

    def increment_usage(self):
        IdScript.objects.filter(id=self.id).update(used=models.F('used') + 1)
        self.used = models.F('used') + 1

    def save(self, *args, **kwargs):
        if not self.script:
            self.script = generate_unique_script_name()
        if not self.key:
            self.key = generate_key()
        super().save(*args, **kwargs)


class Answer(BaseModel):
    script = models.ForeignKey(
        IdScript,
        on_delete=models.CASCADE,
        related_name='answers'
    )
    image = models.ImageField(upload_to='images/')
    answer = models.JSONField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['script', 'created_at']),
        ]

    def __str__(self):
        return f"{self.script.script} - {self.created_at}"


class TgUsers(BaseModel):
    user = models.IntegerField(unique=True)
    is_admin = models.BooleanField(default=False)
    username = models.CharField(max_length=255, null=True, blank=True)

