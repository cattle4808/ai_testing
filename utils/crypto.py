import hashlib
import base64
import urllib.parse
from cryptography.fernet import Fernet

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
