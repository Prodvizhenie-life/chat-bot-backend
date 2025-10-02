import pytest

from .models import ProdvizhenieLifeUser


@pytest.mark.django_db
class TestTelegramAuth:

    def test_init_creates_new_user(self, api_client):
        """POST /init создаёт нового пользователя"""
        headers = {"HTTP_AUTHORIZATION": "TMA new_key"}
        response = api_client.post("/api/auth/init/", **headers)

        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert ProdvizhenieLifeUser.objects.count() == 1

    def test_init_existing_user(self, api_client, tg_user):
        """POST /init возвращает существующего пользователя"""
        headers = {"HTTP_AUTHORIZATION": "TMA 12345"}
        response = api_client.post("/api/auth/init/", **headers)

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "old@example.com"
        assert ProdvizhenieLifeUser.objects.count() == 1

    def test_register_fills_only_empty_fields(self, api_client, tg_user):
        """PUT /register обновляет только пустые поля у пользователя"""
        tg_user.email = "old@example.com"
        tg_user.fio = "Старый Пользователь"
        tg_user.phone = "+71112223344"
        tg_user.save()

        headers = {"HTTP_AUTHORIZATION": "TMA 12345"}
        payload = {
            "email": "new@example.com",
            "fio": "Новый Пользователь",
            "phone": "+79998887766",
        }
        response = api_client.put(
            "/api/auth/register/", payload, format="json", **headers
        )

        assert response.status_code == 200
        data = response.json()

        # В ответе остаются старые данные, новые не перезаписываются
        assert data["email"] == "old@example.com"
        assert data["fio"] == "Старый Пользователь"
        assert data["phone"] == "+71112223344"

        tg_user.refresh_from_db()
        assert tg_user.email == "old@example.com"
        assert tg_user.fio == "Старый Пользователь"
        assert tg_user.phone == "+71112223344"

    def test_register_user_not_found(self, api_client):
        """PUT /register c неверным ключом → 404"""
        headers = {"HTTP_AUTHORIZATION": "TMA wrong_key"}
        payload = {"email": "ghost@example.com", "fio": "Неизвестный"}
        response = api_client.put(
            "/api/auth/register/", payload, format="json", **headers
        )

        assert response.status_code == 404


# @pytest.mark.django_db
# class TestTelegramLinking:
#     """Тесты привязки Telegram"""
#
#     def test_link_telegram_success(self, authenticated_client, telegram_ids):
#         """Успешная привязка Telegram к аккаунту"""
#         url = reverse('link-telegram')
#         response = authenticated_client.post(url, {
#             'telegram_id': telegram_ids['valid']
#         })
#
#         assert response.status_code == status.HTTP_200_OK
#         assert 'успешно привязан' in response.data['detail']
#
#         # Проверяем в БД
#         authenticated_client.user.refresh_from_db()
#         assert authenticated_client.user.telegram_id == telegram_ids['valid']
#
#     def test_link_telegram_without_auth(self, api_client, telegram_ids):
#         """Попытка привязать Telegram без авторизации"""
#         url = reverse('link-telegram')
#         response = api_client.post(url, {
#             'telegram_id': telegram_ids['valid']
#         })
#
#         assert response.status_code == status.HTTP_401_UNAUTHORIZED
#
#     def test_link_already_used_telegram(self, api_client, create_user, telegram_ids):
#         """Попытка привязать уже занятый Telegram ID"""
#         # Первый пользователь с telegram_id
#         user1 = create_user(
#             email='user1@test.com',
#             telegram_id=telegram_ids['valid']
#         )
#
#         # Второй пользователь без telegram_id
#         user2 = create_user(email='user2@test.com')
#
#         # Логинимся за второго
#         response = api_client.post('/api/auth/login/', {
#             'email': 'user2@test.com',
#             'password': 'Pass123!'
#         })
#         token = response.data['access']
#         api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
#
#         # Пытаемся привязать занятый telegram_id
#         url = reverse('link-telegram')
#         response = api_client.post(url, {
#             'telegram_id': telegram_ids['valid']
#         })
#
#         assert response.status_code == status.HTTP_400_BAD_REQUEST
#         assert 'уже привязан' in str(response.data).lower()
#
#     def test_link_second_telegram_to_user(self, authenticated_client, telegram_ids):
#         """Попытка привязать второй Telegram к одному пользователю"""
#         # Привязываем первый
#         authenticated_client.user.telegram_id = telegram_ids['valid']
#         authenticated_client.user.save()
#
#         # Пытаемся привязать второй
#         url = reverse('link-telegram')
#         response = authenticated_client.post(url, {
#             'telegram_id': telegram_ids['another']
#         })
#
#         assert response.status_code == status.HTTP_400_BAD_REQUEST
#         assert 'уже привязан' in str(response.data).lower()
#
#     def test_link_invalid_telegram_id(self, authenticated_client):
#         """Валидация невалидного telegram_id"""
#         url = reverse('link-telegram')
#         response = authenticated_client.post(url, {
#             'telegram_id': -123  # Отрицательный
#         })
#
#         assert response.status_code == status.HTTP_400_BAD_REQUEST
#
#     def test_link_telegram_missing_id(self, authenticated_client):
#         """Попытка привязать без указания telegram_id"""
#         url = reverse('link-telegram')
#         response = authenticated_client.post(url, {})
#
#         assert response.status_code == status.HTTP_400_BAD_REQUEST
#
#
# @pytest.mark.django_db
# class TestTelegramLogin:
#     """Тесты входа через Telegram"""
#
#     def test_login_via_telegram_success(self, api_client, create_user, telegram_ids):
#         """Успешный вход через Telegram ID"""
#         user = create_user(
#             email='user@test.com',
#             telegram_id=telegram_ids['valid']
#         )
#
#         url = reverse('unified-login')
#         response = api_client.post(url, {
#             'telegram_id': telegram_ids['valid']
#         })
#
#         assert response.status_code == status.HTTP_200_OK
#         assert 'access' in response.data
#         assert 'refresh' in response.data
#         assert response.data['user']['telegram_id'] == telegram_ids['valid']
#         assert response.data['user']['email'] == 'user@test.com'
#
#     def test_login_via_unlinked_telegram(self, api_client, telegram_ids):
#         """Попытка входа через непривязанный Telegram"""
#         url = reverse('unified-login')
#         response = api_client.post(url, {
#             'telegram_id': telegram_ids['valid']
#         })
#
#         assert response.status_code == status.HTTP_400_BAD_REQUEST
#         assert 'не найден' in str(response.data).lower()
#
#
# @pytest.mark.django_db
# class TestTelegramUnlinking:
#     """Тесты отвязки Telegram"""
#
#     def test_unlink_telegram_success(self, authenticated_client, telegram_ids):
#         """Успешная отвязка Telegram"""
#         # Сначала привязываем
#         authenticated_client.user.telegram_id = telegram_ids['valid']
#         authenticated_client.user.save()
#
#         url = reverse('unlink-telegram')
#         response = authenticated_client.post(url)
#
#         assert response.status_code == status.HTTP_200_OK
#         assert 'отвязан' in response.data['detail'].lower()
#
#         # Проверяем в БД
#         authenticated_client.user.refresh_from_db()
#         assert authenticated_client.user.telegram_id is None
#
#     def test_unlink_when_no_telegram(self, authenticated_client):
#         """Попытка отвязать когда Telegram не привязан"""
#         url = reverse('unlink-telegram')
#         response = authenticated_client.post(url)
#
#         assert response.status_code == status.HTTP_400_BAD_REQUEST
#         assert 'нет привязанного' in response.data['detail'].lower()
#
#     def test_unlink_without_auth(self, api_client):
#         """Попытка отвязать без авторизации"""
#         url = reverse('unlink-telegram')
#         response = api_client.post(url)
#
#         assert response.status_code == status.HTTP_401_UNAUTHORIZED
#
#
# @pytest.mark.django_db
# class TestValidation:
#     """Тесты валидации входных данных"""
#
#     def test_login_without_credentials(self, api_client):
#         """Вход без данных"""
#         url = reverse('unified-login')
#         response = api_client.post(url, {})
#
#         assert response.status_code == status.HTTP_400_BAD_REQUEST
#
#     def test_login_with_both_methods(self, api_client):
#         """Попытка входа одновременно через email и Telegram"""
#         url = reverse('unified-login')
#         response = api_client.post(url, {
#             'email': 'test@test.com',
#             'password': 'Pass123!',
#             'telegram_id': 123456
#         })
#
#         assert response.status_code == status.HTTP_400_BAD_REQUEST
#
#     def test_login_only_email_without_password(self, api_client):
#         """Вход только с email без пароля"""
#         url = reverse('unified-login')
#         response = api_client.post(url, {
#             'email': 'test@test.com'
#         })
#
#         assert response.status_code == status.HTTP_400_BAD_REQUEST
#
#
# @pytest.mark.django_db
# class TestFullFlow:
#     """Интеграционные тесты полного флоу"""
#
#     def test_full_flow_site_to_telegram(self, api_client, user_data, telegram_ids):
#         """
#         Полный флоу: регистрация на сайте → вход → привязка Telegram →
#         вход через Telegram
#         """
#         # Шаг 1: Регистрация
#         register_url = reverse('user-list')
#         register_response = api_client.post(register_url, user_data)
#         assert register_response.status_code == status.HTTP_201_CREATED
#         user_id = register_response.data['id']
#
#         # Шаг 2: Вход через email
#         login_url = reverse('unified-login')
#         login_response = api_client.post(login_url, {
#             'email': user_data['email'],
#             'password': user_data['password']
#         })
#         assert login_response.status_code == status.HTTP_200_OK
#         access_token = login_response.data['access']
#
#         # Шаг 3: Привязка Telegram
#         api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
#         link_url = reverse('link-telegram')
#         link_response = api_client.post(link_url, {
#             'telegram_id': telegram_ids['valid']
#         })
#         assert link_response.status_code == status.HTTP_200_OK
#
#         # Шаг 4: Вход через Telegram (без токена)
#         api_client.credentials()  # Убираем авторизацию
#         tg_login_response = api_client.post(login_url, {
#             'telegram_id': telegram_ids['valid']
#         })
#         assert tg_login_response.status_code == status.HTTP_200_OK
#         assert tg_login_response.data['user']['id'] == user_id
#         assert tg_login_response.data['user']['telegram_id'] == telegram_ids['valid']
#
#     def test_full_flow_with_unlink(self, api_client, create_user, telegram_ids):
#         """
#         Флоу с отвязкой: вход → привязка → отвязка →
#         попытка входа через Telegram (должна упасть)
#         """
#         # Создаём пользователя
#         user = create_user(email='test@test.com')
#
#         # Вход
#         login_url = reverse('unified-login')
#         login_response = api_client.post(login_url, {
#             'email': 'test@test.com',
#             'password': 'Pass123!'
#         })
#         token = login_response.data['access']
#         api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
#
#         # Привязка
#         link_url = reverse('link-telegram')
#         api_client.post(link_url, {'telegram_id': telegram_ids['valid']})
#
#         # Отвязка
#         unlink_url = reverse('unlink-telegram')
#         unlink_response = api_client.post(unlink_url)
#         assert unlink_response.status_code == status.HTTP_200_OK
#
#         # Попытка входа через Telegram
#         api_client.credentials()  # Убираем токен
#         tg_login_response = api_client.post(login_url, {
#             'telegram_id': telegram_ids['valid']
#         })
#         assert tg_login_response.status_code == status.HTTP_400_BAD_REQUEST
#
#
# @pytest.mark.django_db
# class TestEdgeCases:
#     """Тесты граничных случаев"""
#
#     def test_concurrent_telegram_linking(self, api_client, create_user, telegram_ids):
#         """
#         Проверка race condition при одновременной попытке привязать
#         один telegram_id к разным пользователям
#         """
#         # Создаём двух пользователей
#         user1 = create_user(email='user1@test.com')
#         user2 = create_user(email='user2@test.com')
#
#         # Получаем токены для обоих
#         login_url = reverse('unified-login')
#
#         response1 = api_client.post(login_url, {
#             'email': 'user1@test.com',
#             'password': 'Pass123!'
#         })
#         token1 = response1.data['access']
#
#         response2 = api_client.post(login_url, {
#             'email': 'user2@test.com',
#             'password': 'Pass123!'
#         })
#         token2 = response2.data['access']
#
#         # Первый привязывает
#         api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token1}')
#         link_url = reverse('link-telegram')
#         response = api_client.post(link_url, {
#             'telegram_id': telegram_ids['valid']
#         })
#         assert response.status_code == status.HTTP_200_OK
#
#         # Второй пытается привязать тот же ID
#         api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token2}')
#         response = api_client.post(link_url, {
#             'telegram_id': telegram_ids['valid']
#         })
#         assert response.status_code == status.HTTP_400_BAD_REQUEST
#
#     def test_relink_after_unlink(self, authenticated_client, telegram_ids):
#         """Повторная привязка после отвязки"""
#         link_url = reverse('link-telegram')
#         unlink_url = reverse('unlink-telegram')
#
#         # Привязка
#         response = authenticated_client.post(link_url, {
#             'telegram_id': telegram_ids['valid']
#         })
#         assert response.status_code == status.HTTP_200_OK
#
#         # Отвязка
#         response = authenticated_client.post(unlink_url)
#         assert response.status_code == status.HTTP_200_OK
#
#         # Повторная привязка (того же ID)
#         response = authenticated_client.post(link_url, {
#             'telegram_id': telegram_ids['valid']
#         })
#         assert response.status_code == status.HTTP_200_OK
