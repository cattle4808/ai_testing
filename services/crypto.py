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


import hashlib
import hmac
import json
import time
from urllib.parse import parse_qsl, unquote
from django.conf import settings

import hashlib
import hmac
import json
import time
from urllib.parse import parse_qsl, unquote
from django.conf import settings


class TgCrypto:
    def __init__(self, bot_token: str = None):
        if bot_token is None:
            if not hasattr(settings, "BOT_TOKEN") or settings.BOT_TOKEN is None:
                raise ValueError("BOT_TOKEN is required. Either pass it explicitly or configure Django settings.")
            bot_token = settings.BOT_TOKEN

        # ИСПРАВЛЕНО: Правильная генерация секретного ключа для Web App
        self.SECRET_KEY = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()

    def _parse_init_data(self, init_data: str) -> tuple[dict, str]:
        # ИСПРАВЛЕНО: Используем parse_qsl для правильного парсинга
        try:
            data = dict(parse_qsl(init_data, keep_blank_values=True, strict_parsing=True))
        except ValueError as e:
            print(f"[DEBUG] Failed to parse init_data: {e}")
            return {}, None

        hash_check = data.pop("hash", None)
        data.pop("signature", None)  # Удаляем signature если есть

        # ИСПРАВЛЕНО: Применяем unquote к значениям
        for key, value in data.items():
            data[key] = unquote(value)

        # Нормализация JSON для user
        if "user" in data:
            try:
                user_dict = json.loads(data["user"])
                # ИСПРАВЛЕНО: Правильная сериализация JSON
                data["user"] = json.dumps(user_dict, separators=(",", ":"), sort_keys=True)
            except (json.JSONDecodeError, TypeError) as e:
                print(f"[DEBUG] Failed to normalize user JSON: {e}")

        return data, hash_check

    def _build_check_string(self, data: dict) -> str:
        return "\n".join(f"{k}={v}" for k, v in sorted(data.items()))

    def verify_init_data(self, init_data_str: str, max_age_sec: int = 86400) -> bool:
        try:
            data, hash_check = self._parse_init_data(init_data_str)

            if not hash_check:
                print("[DEBUG] No hash found in init_data")
                return False

            check_string = self._build_check_string(data)

            # ИСПРАВЛЕНО: Правильная последовательность параметров в hmac.new()
            computed_hash = hmac.new(
                self.SECRET_KEY,  # key (первый параметр)
                check_string.encode(),  # msg (второй параметр)
                hashlib.sha256  # digestmod (третий параметр)
            ).hexdigest()

            print(f"[DEBUG] Raw init_data: {init_data_str}")
            print(f"[DEBUG] Parsed data: {data}")
            print(f"[DEBUG] Check string: {repr(check_string)}")
            print(f"[DEBUG] SECRET_KEY (hex): {self.SECRET_KEY.hex()}")
            print(f"[DEBUG] Computed hash: {computed_hash}")
            print(f"[DEBUG] Received hash: {hash_check}")

            if not hmac.compare_digest(computed_hash, hash_check):
                print("[DEBUG] Hash mismatch!")
                return False

            # Проверка времени
            auth_date = data.get("auth_date")
            if not auth_date:
                print("[DEBUG] No auth_date found")
                return False

            try:
                auth_date = int(auth_date)
                now = int(time.time())
                if abs(now - auth_date) > max_age_sec:
                    print(f"[DEBUG] Data too old: {abs(now - auth_date)} seconds")
                    return False
            except (ValueError, TypeError) as e:
                print(f"[DEBUG] Invalid auth_date: {e}")
                return False

            return True

        except Exception as e:
            print(f"[DEBUG] Verification failed with exception: {e}")
            return False


# Альтернативная упрощенная функция (как в рабочих примерах)
def validate_telegram_webapp_data(init_data: str, bot_token: str) -> bool:
    """
    Упрощенная функция валидации на основе рабочих примеров из GitHub
    """
    try:
        # Парсим данные
        hash_string = ""
        init_data_dict = {}

        for chunk in init_data.split("&"):
            key, value = chunk.split("=", 1)
            if key == "hash":
                hash_string = value
                continue
            # Исключаем signature из валидации
            if key == "signature":
                continue
            init_data_dict[key] = unquote(value)

        if not hash_string:
            return False

        # Специальная обработка для photo_url с экранированными слешами
        if "user" in init_data_dict:
            try:
                user_data = json.loads(init_data_dict["user"])
                # ВАЖНО: Сохраняем экранированные слеши в photo_url
                if "photo_url" in user_data and user_data["photo_url"]:
                    user_data["photo_url"] = user_data["photo_url"].replace("/", "\\/")
                init_data_dict["user"] = json.dumps(user_data, separators=(",", ":"), sort_keys=True)
            except json.JSONDecodeError:
                pass

        # Строим строку для проверки
        data_check_string = "\n".join([
            f"{key}={init_data_dict[key]}"
            for key in sorted(init_data_dict.keys())
        ])

        # Генерируем секретный ключ
        secret_key = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()

        # Вычисляем хеш
        computed_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()

        print(f"[DEBUG] Data check string: {repr(data_check_string)}")
        print(f"[DEBUG] Computed hash: {computed_hash}")
        print(f"[DEBUG] Received hash: {hash_string}")

        return computed_hash == hash_string

    except Exception as e:
        print(f"[DEBUG] Validation error: {e}")
        return False


def validate_init_data_strict(init_data: str, bot_token: str) -> bool:
    try:
        from urllib.parse import parse_qs

        init_data_parsed = parse_qs(init_data)
        hash_value = init_data_parsed.get('hash', [None])[0]

        if not hash_value:
            return False

        data_to_check = []
        sorted_items = sorted((key, val[0]) for key, val in init_data_parsed.items()
                              if key not in ['hash', 'signature'])
        data_to_check = [f"{key}={value}" for key, value in sorted_items]

        secret = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()
        computed_hash = hmac.new(secret, "\n".join(data_to_check).encode(), hashlib.sha256).hexdigest()

        print(f"[DEBUG STRICT] Data to check: {data_to_check}")
        joined_data = repr('\\n'.join(data_to_check))
        print(f"[DEBUG STRICT] Joined: {joined_data}")
        print(f"[DEBUG STRICT] Computed: {computed_hash}")
        print(f"[DEBUG STRICT] Received: {hash_value}")

        return computed_hash == hash_value

    except Exception as e:
        print(f"[DEBUG STRICT] Error: {e}")
        return False


import hashlib
import hmac
from urllib.parse import parse_qsl, unquote


def validate_init_data_hybrid(init_data: str, bot_token: str) -> bool:
    """
    Гибридный метод - комбинация URL-декодирования и сохранения оригинальной структуры
    """
    try:
        hash_value = None
        data_dict = {}

        # Ручной парсинг
        for chunk in init_data.split("&"):
            if "=" not in chunk:
                continue
            key, value = chunk.split("=", 1)
            if key == "hash":
                hash_value = value
            elif key != "signature":
                # Частично декодируем только определенные символы
                if key == "user":
                    # Для user декодируем только основные символы, но оставляем экранированные слеши
                    value_decoded = unquote(value)
                    # Возвращаем экранированные слеши
                    value_decoded = value_decoded.replace("/", "\\/")
                    data_dict[key] = value_decoded
                else:
                    # Для остальных полей полное декодирование
                    data_dict[key] = unquote(value)

        if not hash_value:
            return False

        # Формируем строку для проверки
        data_check_string = "\n".join(f"{key}={value}" for key, value in sorted(data_dict.items()))

        # Генерируем секрет и хеш
        secret = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()
        computed_hash = hmac.new(secret, data_check_string.encode(), hashlib.sha256).hexdigest()

        print(f"[HYBRID] Data check string: {repr(data_check_string)}")
        print(f"[HYBRID] Computed hash: {computed_hash}")
        print(f"[HYBRID] Received hash: {hash_value}")

        return computed_hash == hash_value

    except Exception as e:
        print(f"[HYBRID] Error: {e}")
        return False


def validate_init_data_test_variants(init_data: str, bot_token: str) -> bool:
    """
    Тестируем разные варианты обработки user поля
    """
    try:
        hash_value = None
        data_dict = {}

        # Парсим основные данные
        for chunk in init_data.split("&"):
            if "=" not in chunk:
                continue
            key, value = chunk.split("=", 1)
            if key == "hash":
                hash_value = value
            elif key != "signature":
                if key != "user":
                    data_dict[key] = unquote(value)
                else:
                    # Сохраняем raw user для тестирования
                    user_raw = value

        if not hash_value:
            return False

        # Тестируем разные варианты обработки user
        user_variants = [
            user_raw,  # 1. Как есть (URL-кодированный)
            unquote(user_raw),  # 2. Полностью декодированный
            unquote(user_raw).replace("/", "\\/"),  # 3. Декодированный + экранированные слеши
        ]

        secret = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()

        for i, user_variant in enumerate(user_variants, 1):
            test_data = dict(data_dict)
            test_data["user"] = user_variant

            data_check_string = "\n".join(f"{key}={value}" for key, value in sorted(test_data.items()))
            computed_hash = hmac.new(secret, data_check_string.encode(), hashlib.sha256).hexdigest()

            print(f"[VARIANT {i}] User: {repr(user_variant[:50])}...")
            print(f"[VARIANT {i}] Hash: {computed_hash}")

            if computed_hash == hash_value:
                print(f"[SUCCESS] Variant {i} matches!")
                return True

        print(f"[TARGET] Expected: {hash_value}")
        return False

    except Exception as e:
        print(f"[TEST] Error: {e}")
        return False


def validate_init_data_correct(init_data: str, bot_token: str) -> bool:
    """
    ПРАВИЛЬНАЯ валидация Telegram Web App initData
    """
    try:
        # Парсим как query string (НЕ используем parse_qs!)
        # parse_qsl не URL-декодирует значения автоматически
        data_pairs = parse_qsl(init_data, keep_blank_values=True)

        hash_value = None
        data_to_check = []

        # Собираем данные и ищем hash
        for key, value in data_pairs:
            if key == "hash":
                hash_value = value
            elif key != "signature":  # Исключаем signature
                data_to_check.append((key, value))

        if not hash_value:
            return False

        # Сортируем по ключам и формируем строку
        data_to_check.sort(key=lambda x: x[0])
        data_check_string = "\n".join(f"{key}={value}" for key, value in data_to_check)

        # Генерируем секрет
        secret = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()

        # Вычисляем хеш
        computed_hash = hmac.new(secret, data_check_string.encode(), hashlib.sha256).hexdigest()

        print(f"[DEBUG] Data check string: {repr(data_check_string)}")
        print(f"[DEBUG] Computed hash: {computed_hash}")
        print(f"[DEBUG] Received hash: {hash_value}")

        return computed_hash == hash_value

    except Exception as e:
        print(f"[DEBUG] Validation error: {e}")
        return False


def validate_init_data_manual(init_data: str, bot_token: str) -> bool:
    """
    Альтернативная валидация - ручной парсинг без URL-декодирования
    """
    try:
        hash_value = None
        data_dict = {}

        # Ручной парсинг без URL-декодирования
        for chunk in init_data.split("&"):
            if "=" not in chunk:
                continue
            key, value = chunk.split("=", 1)
            if key == "hash":
                hash_value = value
            elif key != "signature":
                data_dict[key] = value

        if not hash_value:
            return False

        # Формируем строку для проверки
        data_check_string = "\n".join(f"{key}={value}" for key, value in sorted(data_dict.items()))

        # Генерируем секрет и хеш
        secret = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()
        computed_hash = hmac.new(secret, data_check_string.encode(), hashlib.sha256).hexdigest()

        print(f"[MANUAL] Data check string: {repr(data_check_string)}")
        print(f"[MANUAL] Computed hash: {computed_hash}")
        print(f"[MANUAL] Received hash: {hash_value}")

        return computed_hash == hash_value

    except Exception as e:
        print(f"[MANUAL] Error: {e}")
        return False