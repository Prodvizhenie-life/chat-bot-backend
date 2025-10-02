import time
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings
from .models import ProdvizhenieLifeUser
from .serializers import UserSerializer, UnifiedLoginSerializer, UserCreateSerializer
from .utils import verify_tma


class InitView(APIView):
    """
    Универсальная точка входа для проверки авторизации.

    Поддерживает два типа авторизации:
    1. TMA (Telegram Mini Apps): Header `Authorization: TMA <initData>`
    2. Bearer JWT: Header `Authorization: Bearer <token>`

    Returns:
        200: Данные пользователя + токены
        401: Невалидные credentials
        404: Пользователь не найден (для TMA)
    """

    def post(self, request):
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return Response(
                {"detail": "Authentication credentials were not provided."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # 1. Telegram Mini Apps flow
        if auth_header.startswith("TMA "):
            init_data = auth_header.split(" ", 1)[1]

            # Валидируем initData через aiogram
            webapp_data = verify_tma(init_data)
            if not webapp_data:
                return Response(
                    {"detail": "Invalid or expired TMA initData"},
                    status=status.HTTP_401_UNAUTHORIZED
                )

            # Извлекаем telegram_id из validated data
            if not webapp_data.user:
                return Response(
                    {"detail": "User data not found in TMA initData"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            telegram_id = webapp_data.user.id

            # Ищем пользователя
            user = ProdvizhenieLifeUser.objects.filter(
                telegram_id=telegram_id
            ).first()
            if not user:
                return Response(
                    {"detail": "Пользователь не найден. "
                               "Зарегистрируйтесь через /api/register/"},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Возвращаем данные + токены для последующих запросов
            refresh = RefreshToken.for_user(user)
            return Response({
                "user": UserSerializer(user).data,
                "access": str(refresh.access_token),
                "refresh": str(refresh)
            }, status=status.HTTP_200_OK)

        # 2. Bearer JWT flow
        if auth_header.startswith("Bearer "):
            if request.user and request.user.is_authenticated:
                return Response(
                    UserSerializer(request.user).data,
                    status=status.HTTP_200_OK
                )
            return Response(
                {"detail": "Invalid token"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        return Response(
            {"detail": "Unsupported authorization type"},
            status=status.HTTP_400_BAD_REQUEST
        )


class RegisterView(APIView):
    """
    Регистрация новых пользователей.

    Поддерживает два способа:
    1. Email/password регистрация (для веб-виджета)
       Body: { email, password, fio, phone }

    2. Telegram регистрация (для Mini Apps)
       Header: Authorization: TMA <initData>
       Автоматически извлекает данные из Telegram

    Returns:
        201: Пользователь создан
        200: Пользователь уже существует (для TMA)
        400: Невалидные данные
        401: Невалидная TMA подпись
    """

    def post(self, request):
        auth_header = request.headers.get("Authorization")

        # --- Регистрация через Telegram Mini Apps ---
        if auth_header and auth_header.startswith("TMA "):
            init_data = auth_header.split(" ", 1)[1]

            # Валидируем через aiogram
            webapp_data = verify_tma(init_data)
            if not webapp_data:
                return Response(
                    {"detail": "Invalid or expired TMA initData"},
                    status=status.HTTP_401_UNAUTHORIZED
                )

            # Извлекаем данные пользователя
            if not webapp_data.user:
                return Response(
                    {"detail": "User data not found in TMA initData"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            tg_user = webapp_data.user
            telegram_id = tg_user.id

            # Проверяем, существует ли юзер
            user = ProdvizhenieLifeUser.objects.filter(telegram_id=telegram_id).first()
            if user:
                # Пользователь уже есть — возвращаем его данные
                refresh = RefreshToken.for_user(user)
                return Response({
                    "user": UserSerializer(user).data,
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                    "message": "Пользователь уже зарегистрирован"
                }, status=status.HTTP_200_OK)

            # Создаём нового пользователя из Telegram
            user = ProdvizhenieLifeUser.objects.create(
                telegram_id=telegram_id,
                email=f"tg{telegram_id}@prodvizhenie.life",  # временный email
                fio=tg_user.first_name or "Telegram User",
                phone="",  # будет заполнено позже
                first_name=tg_user.first_name or "",
                last_name=tg_user.last_name or "",
                username=tg_user.username or "",
                language_code=tg_user.language_code or "",
                is_auth_tg=True
            )

            refresh = RefreshToken.for_user(user)
            return Response({
                "user": UserSerializer(user).data,
                "access": str(refresh.access_token),
                "refresh": str(refresh)
            }, status=status.HTTP_201_CREATED)

        # --- Регистрация через email/password ---
        if not request.data.get("email") or not request.data.get("password"):
            return Response(
                {"detail": "Email и пароль обязательны"},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = UserCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Сразу выдаём токены после регистрации
        refresh = RefreshToken.for_user(user)
        return Response({
            "user": UserSerializer(user).data,
            "access": str(refresh.access_token),
            "refresh": str(refresh)
        }, status=status.HTTP_201_CREATED)


class UnifiedLoginView(APIView):
    """
    Универсальный логин для пользователей.

    Поддерживает вход через:
    - Email + password
    - Telegram ID (если аккаунт привязан)

    При успешном входе токены устанавливаются в httpOnly cookies.

    Body: { email, password } или { telegram_id }

    Returns:
        200: Успешный вход + cookies с токенами
        400: Невалидные данные
        401: Неверные credentials
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = UnifiedLoginSerializer(
            data=request.data,
            context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]

        # Генерируем токены
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        # Формируем ответ
        resp = Response({
            "detail": "Successfully logged in",
            "user": UserSerializer(user).data
        })

        # Устанавливаем cookies
        secure = getattr(settings, 'SECURE_COOKIES', not settings.DEBUG)
        resp.set_cookie(
            "access",
            access_token,
            httponly=True,
            secure=secure,
            samesite="Strict",
            max_age=1800  # 30 минут
        )
        resp.set_cookie(
            "refresh",
            refresh_token,
            httponly=True,
            secure=secure,
            samesite="Strict",
            max_age=86400  # 24 часа
        )
        return resp


class RefreshTokenView(APIView):
    """
    Обновление access токена через refresh токен из cookies.

    Returns:
        200: Новый access токен в cookies
        401: Refresh токен отсутствует или невалиден
    """
    def post(self, request):
        refresh_token = request.COOKIES.get("refresh")

        if not refresh_token:
            return Response(
                {"detail": "Refresh token not found"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        try:
            token = RefreshToken(refresh_token)
            access_token = str(token.access_token)
        except Exception:
            return Response(
                {"detail": "Invalid refresh token"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        resp = Response({"detail": "Token refreshed"})
        secure = getattr(settings, 'SECURE_COOKIES', not settings.DEBUG)
        resp.set_cookie(
            "access",
            access_token,
            httponly=True,
            secure=secure,
            samesite="Strict",
            max_age=1800
        )
        return resp


class LogoutView(APIView):
    """
    Выход из системы — удаление токенов из cookies.

    Returns:
        200: Успешный выход
    """
    def post(self, request):
        resp = Response({"detail": "Successfully logged out"})
        resp.delete_cookie("access")
        resp.delete_cookie("refresh")
        return resp
