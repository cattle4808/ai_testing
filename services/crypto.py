import hashlib
import base64
import urllib.parse
import hmac
from cryptography.fernet import Fernet
import time

try:
    from django.conf import settings
    _DEFAULT_SECRET_KEY = settings.SECRET_KEY
except ImportError:
    _DEFAULT_SECRET_KEY = None



class SimpleCipher:
    def __init__(self, secret_key: str = None):
        if secret_key is None:
            if _DEFAULT_SECRET_KEY is None:
                raise ValueError("SECRET_KEY is required. Either pass it explicitly or configure Django settings.")
            secret_key = _DEFAULT_SECRET_KEY

        key = hashlib.sha256(secret_key.encode()).digest()
        self.key = base64.urlsafe_b64encode(key)
        self.cipher = Fernet(self.key)

    def encrypt(self, plaintext: str) -> str:
        return self.cipher.encrypt(plaintext.encode()).decode()

    def encrypt_for_url(self, plaintext: str) -> str:
        token = self.encrypt(plaintext)
        return urllib.parse.quote(token)

    def decrypt(self, token: str) -> str:
        token = urllib.parse.unquote(token)
        return self.cipher.decrypt(token.encode()).decode()

class TgCrypto:
    def __init__(self, bot_token: str = None):
        if bot_token is None:
            if not hasattr(settings, "BOT_TOKEN") or settings.BOT_TOKEN is None:
                raise ValueError("BOT_TOKEN is required. Either pass it explicitly or configure Django settings.")
            bot_token = settings.BOT_TOKEN
        self.SECRET_KEY = hashlib.sha256(bot_token.encode()).digest()

    def parse_init_data(self, init_data: str) -> tuple[dict, str]:
        data = dict(urllib.parse.parse_qsl(init_data, keep_blank_values=True))
        hash_check = data.pop("hash", None)
        return data, hash_check

    def build_check_string(self, data: dict) -> str:
        return "\n".join(f"{k}={v}" for k, v in sorted(data.items()))

    def verify_init_data(self, init_data_str: str, max_age_sec: int = 86400) -> bool:
        data, hash_check = self.parse_init_data(init_data_str)
        check_string = self.build_check_string(data)
        computed_hash = hmac.new(self.SECRET_KEY, check_string.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(computed_hash, hash_check):
            return False
        auth_date = int(data.get("auth_date", 0))
        now = int(time.time())
        if abs(now - auth_date) > max_age_sec:
            return False
        return True


