from rest_framework import serializers
from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer

User = get_user_model()


class UserCreateSerializer(BaseUserCreateSerializer):
    """
    Сериализатор для регистрации новых пользователей через email/password.

    Используется в RegisterView для создания аккаунтов через веб-виджет.
    Валидирует все обязательные поля и создаёт пользователя с зашифрованным паролем.
    """

    class Meta(BaseUserCreateSerializer.Meta):
        model = User
        fields = ("id", "email", "password", "fio", "phone")
        extra_kwargs = {
            "email": {"required": True},
            "password": {"write_only": True, "required": True, "min_length": 8},
            "fio": {"required": True, "min_length": 2},
            "phone": {"required": True},
        }


class UserSerializer(serializers.ModelSerializer):
    """
    Базовый сериализатор для отображения данных пользователя.

    Используется для:
    - Возврата данных после авторизации
    - GET /api/users/me/
    - Списка пользователей (для админов)

    Все поля опциональны для PATCH запросов.
    """

    class Meta:
        model = User
        fields = ["id", "email", "fio", "phone", "telegram_id", "role"]
        read_only_fields = ["id", "role"]  # role меняется только админами
        extra_kwargs = {
            "email": {"required": False},
            "fio": {"required": False},
            "phone": {"required": False},
        }


class LinkTelegramSerializer(serializers.Serializer):
    """
    Сериализатор для привязки Telegram аккаунта к существующему пользователю.

    Валидирует:
    - telegram_id > 0
    - telegram_id не занят другим пользователем
    - у текущего пользователя ещё нет привязанного Telegram
    """

    telegram_id = serializers.IntegerField()

    def validate_telegram_id(self, value):
        """Проверка валидности telegram_id."""
        if value <= 0:
            raise serializers.ValidationError("Telegram ID должен быть положительным числом")

        if User.objects.filter(telegram_id=value).exists():
            raise serializers.ValidationError(
                "Этот Telegram аккаунт уже привязан к другому пользователю"
            )

        return value

    def validate(self, attrs):
        """Проверка, что у пользователя ещё нет привязанного Telegram."""
        user = self.context['request'].user

        if user.telegram_id:
            raise serializers.ValidationError({
                "telegram_id": "У вас уже привязан Telegram. Сначала отвяжите текущий аккаунт."
            })

        return attrs


class UnifiedLoginSerializer(serializers.Serializer):
    """
    Универсальный сериализатор для входа в систему.

    Поддерживает два способа авторизации:
    1. Email + password (для веб-виджета)
    2. Telegram ID (для пользователей с привязанным Telegram)

    Возвращает в validated_data поле "user" с объектом пользователя.
    """

    email = serializers.EmailField(required=False)
    password = serializers.CharField(required=False, write_only=True)
    telegram_id = serializers.IntegerField(required=False)

    def validate(self, attrs):
        """
        Валидация credentials и поиск пользователя.

        Raises:
            ValidationError: Если credentials невалидны или отсутствуют
        """
        email = attrs.get("email")
        password = attrs.get("password")
        telegram_id = attrs.get("telegram_id")

        # Проверка: должен быть указан хотя бы один способ входа
        if not ((email and password) or telegram_id):
            raise serializers.ValidationError(
                "Укажите либо email и password, либо telegram_id"
            )

        # Проверка: нельзя указывать оба способа одновременно
        if email and password and telegram_id:
            raise serializers.ValidationError(
                "Укажите только один способ входа"
            )

        user = None

        # Вход через email/password
        if email and password:
            user = User.objects.filter(email__iexact=email).first()

            if not user or not user.check_password(password):
                raise serializers.ValidationError({
                    "detail": "Неверный email или пароль"
                })

        # Вход через Telegram ID
        elif telegram_id:
            try:
                user = User.objects.get(telegram_id=telegram_id)
            except User.DoesNotExist:
                raise serializers.ValidationError({
                    "detail": (
                        "Пользователь с таким Telegram аккаунтом не найден. "
                        "Сначала зарегистрируйтесь или привяжите Telegram к существующему аккаунту."
                    )
                })

        # Финальная проверка активности пользователя
        if not user or not user.is_active:
            raise serializers.ValidationError({
                "detail": "Невозможно войти. Аккаунт неактивен или заблокирован."
            })

        attrs["user"] = user
        return attrs
