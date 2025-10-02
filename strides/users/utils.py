import hashlib
import hmac
from urllib.parse import parse_qsl
import json
from django.conf import settings

def verify_tma(init_data: str) -> dict | None:
    """
    Проверяет initData от Telegram Mini Apps.
    Возвращает dict с user, если подпись валидна, иначе None.
    """
    # Разбираем строку вида "user=...&auth_date=...&hash=..."
    data = dict(parse_qsl(init_data, strict_parsing=True))
    hash_received = data.pop("hash", None)
    if not hash_received:
        return None

    # Готовим строку для подписи
    data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(data.items()))

    # Считаем секретный ключ = sha256(bot_token)
    secret_key = hashlib.sha256(settings.TELEGRAM_BOT_TOKEN.encode()).digest()

    # Делаем HMAC-SHA256
    calculated_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()

    if calculated_hash != hash_received:
        return None

    return data
