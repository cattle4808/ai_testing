from datetime import datetime
from django.forms.models import model_to_dict

from api.v1 import models
from . import catch_error


@catch_error("ERR_GET_OR_CREATE_USER")
def get_or_create_tg_user(user_id: int, ref_by: int = None) -> dict:
    user, created = models.TgUsers.objects.get_or_create(user=user_id)

    if created and ref_by:
        try:
            ref_user = models.TgUsers.objects.get(user=ref_by)
            user.referred_by = ref_user
            user.save()
        except models.TgUsers.DoesNotExist:
            print(f"[⚠️] Реферал с user_id={ref_by} не найден в базе.")

    return model_to_dict(user)



@catch_error("ERR_CREATE_SCRIPT")
def create_script(owner: models.TgUsers, start_at: datetime, stop_at: datetime) -> dict:
    def_get_refferals = models.Referral.objects.filter(inviter=owner, used=False)
    if def_get_refferals.exists():
        referral = def_get_refferals.first()
        referral.used = True
        referral.save()

    script = models.IdScript.objects.create(
        owner=owner,
        start_at=start_at,
        stop_at=stop_at,
    )
    data = model_to_dict(script, fields=[
        'id', 'script', 'key', 'script_type', 'fingerprint',
        'start_at', 'stop_at', 'is_active', 'used',
        'max_usage', 'first_activate', 'first_seen'
    ])
    data['owner_id'] = script.owner_id
    return data


@catch_error("ERR_ADD_TO_REFERRAL")
def add_to_referral(inviter, invited) -> dict:
    ref = models.Referral.objects.create(inviter=inviter, invited=invited)
    data = model_to_dict(ref, fields=['id', 'used', 'created_at'])
    data['inviter_user_id'] = ref.inviter.user_id
    data['invited_user_id'] = ref.invited.user_id
    return data


@catch_error("ERR_CHANGE_SCRIPT_STATUS")
def change_script_status(key, is_active: bool) -> dict:
    script = models.IdScript.objects.get(key=key)
    script.is_active = is_active
    script.save()
    data = model_to_dict(script, fields=[
        'id', 'script', 'key', 'script_type', 'fingerprint',
        'start_at', 'stop_at', 'is_active', 'used',
        'max_usage', 'first_activate', 'first_seen'
    ])
    data['owner_id'] = script.owner_id
    return data


@catch_error("ERR_GET_MY_SCRIPTS")
def get_my_scripts(user_id: int) -> list:
    scripts = models.IdScript.objects.filter(owner_id=user_id)
    return [model_to_dict(script, fields=[
        'id', 'script', 'key', 'script_type', 'fingerprint',
        'start_at', 'stop_at', 'is_active', 'used',
        'max_usage', 'first_activate', 'first_seen'
    ]) for script in scripts]


@catch_error("ERR_GET_REFERRALS_COUNTS")
def get_referrals_counts(user_id: int) -> dict:
    referrals = models.Referral.objects.filter(inviter_id=user_id)
    all_referrals = [
        model_to_dict(ref, fields=['id', 'used', 'created_at']) for ref in referrals
    ]
    used_referrals = [
        model_to_dict(ref, fields=['id', 'used', 'created_at']) for ref in referrals if ref.used
    ]
    unused_referrals = [
        model_to_dict(ref, fields=['id', 'used', 'created_at']) for ref in referrals if not ref.used
    ]
    return {
        "all": all_referrals,
        "used": used_referrals,
        "unused": unused_referrals,
    }


@catch_error("ERR_GET_REFERRAL_INVITERS")
def get_referrals_inviters(user_id: int):
    users = models.TgUsers.objects.filter(referred_by=user_id)
    return [model_to_dict(user, fields=['user', 'is_admin', 'username', 'referred_by']) for user in users]

@catch_error("IS_ADMIN")
def is_admin(user_id: int) -> bool:
    return models.TgUsers.objects.filter(user=user_id, is_admin=True).exists()