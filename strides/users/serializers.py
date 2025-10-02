from rest_framework import serializers
from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer, UserSerializer as BaseUserSerializer

from .models import ProdvizhenieLifeUser

User = get_user_model()


# --- Регистрация через Djoser ---
class UserCreateSerializer(BaseUserCreateSerializer):

    class Meta(BaseUserCreateSerializer.Meta):
        model = User
        fields = ("id", "email", "password", "fio", "phone")
        extra_kwargs = {
            "email": {"required": True},
            "password": {"write_only": True, "required": True},
            "fio": {"required": True},
            "phone": {"required": True},
        }


# --- Базовый сериализатор для Djoser ---
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProdvizhenieLifeUser
        fields = ["id", "email", "fio", "phone", "telegram_id"]
        extra_kwargs = {
            "email": {"required": False},
            "fio": {"required": False},
            "phone": {"required": False},
        }


# --- Кастомный для CRUD (ModelViewSet и т.п.) ---
class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email", "fio", "telegram_id", "role", "password")
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user


class LinkTelegramSerializer(serializers.Serializer):
    telegram_id = serializers.IntegerField()

    def validate_telegram_id(self, value):
        if value <= 0:
            raise serializers.ValidationError("Неверный telegram_id")
        if User.objects.filter(telegram_id=value).exists():
            raise serializers.ValidationError("Этот Telegram уже привязан к другому аккаунту")
        return value

    def validate(self, attrs):
        user = self.context['request'].user
        if user.telegram_id:
            raise serializers.ValidationError(
                {"telegram_id": "У вас уже привязан Telegram. Сначала отвяжите текущий."}
            )
        return attrs


class UnifiedLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=False)
    password = serializers.CharField(required=False, write_only=True)
    telegram_id = serializers.IntegerField(required=False)

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")
        telegram_id = attrs.get("telegram_id")

        if not ((email and password) or telegram_id):
            raise serializers.ValidationError("Укажите email+password или telegram_id")

        if email and password and telegram_id:
            raise serializers.ValidationError("Укажите только один способ входа")

        user = None

        if email and password:
            user = User.objects.filter(email__iexact=email).first()
            if not user or not user.check_password(password):
                raise serializers.ValidationError({"detail": "Неверный email или пароль"})

        elif telegram_id:
            try:
                user = User.objects.get(telegram_id=telegram_id)
            except User.DoesNotExist:
                raise serializers.ValidationError(
                    {"detail": "Пользователь с таким Telegram не найден. Сначала зарегистрируйтесь."}
                )

        if not user or not user.is_active:
            raise serializers.ValidationError({"detail": "Невозможно войти с предоставленными данными"})

        attrs["user"] = user
        return attrs
