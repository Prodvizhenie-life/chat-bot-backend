from aiogram.utils.web_app import safe_parse_webapp_init_data
from aiogram.types import WebAppData
from django.conf import settings
from typing import Optional, Dict
import time


def verify_tma(
    init_data: str,
    max_age: int = 3600
) -> Optional[WebAppData]:
    """
    Проверяет подлинность initData от Telegram Mini Apps используя aiogram.

    Выполняет следующие проверки:
    1. Валидация HMAC-SHA256 подписи (через aiogram)
    2. Проверка времени auth_date (защита от replay attacks)

    Args:
        init_data: Строка initData в формате URL query string.
                   Пример: "user={...}&auth_date=1234567890&hash=abc123..."
        max_age: Максимальный возраст данных в секундах (по умолчанию 1 час).

    Returns:
        WebAppInitData объект с полями (user, auth_date, и т.д.)
        если валидация успешна.
        None если подпись невалидна или данные устарели.
    """
    # Проверка наличия bot token
    bot_token = getattr(settings, 'TELEGRAM_BOT_TOKEN', None)
    if not bot_token:
        raise ValueError(
            "TELEGRAM_BOT_TOKEN не настроен в Django settings. "
            "Добавьте TELEGRAM_BOT_TOKEN = 'your_bot_token' в settings.py"
        )

    try:
        # Валидируем initData через aiogram
        # safe_parse_webapp_init_data автоматически проверяет HMAC подпись
        webapp_data = safe_parse_webapp_init_data(
            token=bot_token,
            init_data=init_data
        )

        # Проверка времени (защита от replay attacks)
        if webapp_data.auth_date:
            auth_timestamp = int(webapp_data.auth_date.timestamp())
            current_timestamp = int(time.time())

            if current_timestamp - auth_timestamp > max_age:
                # Данные устарели
                return None

        return webapp_data

    except (ValueError, Exception):
        # Невалидная подпись или некорректный формат данных
        return None


def extract_telegram_user(init_data: str) -> Optional[Dict]:
    """
    Извлекает данные пользователя Telegram из валидированного initData.

    Args:
        init_data: Строка initData от Telegram Mini Apps

    Returns:
        Dict с полями:
        - id: Telegram ID пользователя (int)
        - first_name: Имя (str, optional)
        - last_name: Фамилия (str, optional)
        - username: Username (str, optional)
        - language_code: Код языка (str, optional)
        - photo_url: URL фото (str, optional)

        None если данные невалидны
    """
    # Валидируем initData
    webapp_data = verify_tma(init_data)
    if not webapp_data or not webapp_data.user:
        return None

    user = webapp_data.user

    return {
        "id": user.id,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "username": user.username,
        "language_code": user.language_code,
        "photo_url": getattr(user, 'photo_url', None)
    }


def is_tma_valid(init_data: str, max_age: int = 3600) -> bool:
    """
    Быстрая проверка валидности TMA initData.

    Args:
        init_data: Строка initData от Telegram
        max_age: Максимальный возраст в секундах

    Returns:
        True если initData валидна, False иначе
    """
    return verify_tma(init_data, max_age) is not None
