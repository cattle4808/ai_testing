import hashlib
import base64
import json
import urllib.parse
import hmac
from cryptography.fernet import Fernet
import time
from django.conf import settings



SECRET_KEY = settings.SECRET_KEY

class SimpleCipher:
    def __init__(self, secret_key: str = None):
        if secret_key is None:
            if SECRET_KEY is None:
                raise ValueError("SECRET_KEY is required. Either pass it explicitly or configure Django settings.")
            secret_key = SECRET_KEY

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

class CompactReferralCipher:
    def __init__(self, secret_key: str = None):
        if secret_key is None:
            if SECRET_KEY is None:
                raise ValueError("SECRET_KEY is required.")
            secret_key = SECRET_KEY
        self.secret_key = secret_key.encode()

    def encrypt_id(self, user_id: int) -> str:
        id_bytes = str(user_id).encode()
        signature = hmac.new(self.secret_key, id_bytes, hashlib.sha256).digest()[:4]
        token = base64.urlsafe_b64encode(id_bytes + signature).decode().rstrip("=")
        return token

    def decrypt_id(self, token: str) -> int | None:
        try:
            padded = token + "=" * (-len(token) % 4)
            decoded = base64.urlsafe_b64decode(padded)
            user_id_bytes, signature = decoded[:-4], decoded[-4:]
            expected = hmac.new(self.secret_key, user_id_bytes, hashlib.sha256).digest()[:4]
            if hmac.compare_digest(signature, expected):
                return int(user_id_bytes.decode())
        except Exception:
            pass
        return None




class TgCrypto:
    def __init__(self, bot_token: str = None):
        if bot_token is None:
            if not hasattr(settings, "BOT_TOKEN") or settings.BOT_TOKEN is None:
                raise ValueError("BOT_TOKEN is required. Either pass it explicitly or configure Django settings.")
            bot_token = settings.BOT_TOKEN
        self.SECRET_KEY = hashlib.sha256(bot_token.encode()).digest()

    def _parse_init_data(self, init_data: str) -> tuple[dict, str]:
        data = dict(urllib.parse.parse_qsl(init_data, keep_blank_values=True))
        hash_check = data.pop("hash", None)
        data.pop("signature", None)

        if "user" in data:
            try:
                user_dict = json.loads(data["user"])
                data["user"] = json.dumps(user_dict, separators=(",", ":"), sort_keys=True)
            except Exception as e:
                print(f"[DEBUG] Failed to normalize user JSON: {e}")

        return data, hash_check

    def _build_check_string(self, data: dict) -> str:
        return "\n".join(f"{k}={v}" for k, v in sorted(data.items()))

    def verify_init_data(self, init_data_str: str, max_age_sec: int = 86400) -> bool:
        data, hash_check = self._parse_init_data(init_data_str)
        check_string = self._build_check_string(data)
        computed_hash = hmac.new(self.SECRET_KEY, check_string.encode(), hashlib.sha256).hexdigest()

        print("[DEBUG] check_string:", check_string)
        print("[DEBUG] computed_hash:", computed_hash)
        print("[DEBUG] received_hash:", hash_check)

        if not hmac.compare_digest(computed_hash, hash_check):
            return False

        auth_date = int(data.get("auth_date", 0))
        now = int(time.time())
        if abs(now - auth_date) > max_age_sec:
            return False
        return True
# user_id = 6435079512
#
#
# cipher = CompactReferralCipher()
#
# code = cipher.encrypt_id(user_id)
# print("🔐 Encrypted code:", code)
#
# decoded = cipher.decrypt_id(code)
# print("🔓 Decrypted user_id:", decoded)
#
# from django.conf import settings
# print(settings.SECRET_KEY)

