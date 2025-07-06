from services.crypto import SimpleCipher
from django.conf import settings



def generate_referral_link(user_id: int) -> str:
    cipher = SimpleCipher()
    referral_code = cipher.encrypt_for_url(str(user_id))

    bot_username = settings.BOT_USERNAME
    referral_url = f"https://t.me/{bot_username}?start={referral_code}"

    return referral_url

