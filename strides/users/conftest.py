import pytest
from rest_framework.test import APIClient

from .models import ProdvizhenieLifeUser


@pytest.fixture
def api_client():
    """Базовый API клиент"""
    return APIClient()


@pytest.fixture
def user_data():
    """Стандартные данные пользователя для тестов"""
    return {
        'email': 'test@example.com',
        'password': 'TestPass123!',
        'fio': 'Тестовый Пользователь',
    }


@pytest.fixture
def create_user(db):
    """Фабрика для создания пользователей"""

    def _create_user(**kwargs):
        defaults = {
            'email': 'user@example.com',
            'password': 'Pass123!',
            'fio': 'Test',
        }
        defaults.update(kwargs)
        return ProdvizhenieLifeUser.objects.create_user(**defaults)

    return _create_user


@pytest.fixture
def tg_user(db):
    return ProdvizhenieLifeUser.objects.create(
        email="old@example.com",
        fio="Старый Пользователь",
        telegram_id="12345",
        is_auth_tg=True,
    )


@pytest.fixture
def authenticated_client_bearer(api_client, create_user):
    """
    Клиент с JWT Bearer авторизацией (имитация входа с сайта)
    """
    user = create_user()
    response = api_client.post(
        '/api/auth/login/', {'email': user.email, 'password': 'Pass123!'}
    )
    token = response.data['access']
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    api_client.user = user
    return api_client


@pytest.fixture
def authenticated_client_tma(api_client, create_user):
    """
    Клиент с TMA-авторизацией (имитация входа через Telegram Mini App).
    В реальности TMA заголовок формируется Telegram SDK,
    здесь просто заглушка для тестов.
    """
    user = create_user(telegram_id=111111111)
    api_client.credentials(HTTP_AUTHORIZATION='TMA valid_tma_key')
    api_client.user = user
    return api_client


@pytest.fixture
def telegram_ids():
    """Набор Telegram ID для тестов"""
    return {'valid': 123456789, 'another': 987654321, 'third': 555555555}
