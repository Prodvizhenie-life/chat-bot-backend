import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework_simplejwt.tokens import RefreshToken
from .models import ProdvizhenieLifeUser
from .serializers import UserSerializer, UnifiedLoginSerializer, UserCreateSerializer
from .utils import verify_tma


def get_tma_key(request):
    auth_header = request.headers.get("Authorization")
    return auth_header.split(" ", 1)[1] if auth_header and auth_header.startswith("TMA ") else None

class InitView(APIView):
    """
    POST /api/auth/init/
    Универсальная точка входа
    """
    def post(self, request):
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return Response({"detail": "Authentication credentials were not provided."},
                            status=status.HTTP_401_UNAUTHORIZED)

        # 1. Telegram flow
        if auth_header.startswith("TMA "):
            tma_key = auth_header.split(" ", 1)[1]
            user = ProdvizhenieLifeUser.objects.filter(telegram_id=tma_key).first()
            if not user:
                return Response(
                    {"detail": "Пользователь не найден, зарегистрируйтесь сперва"},
                    status=status.HTTP_404_NOT_FOUND
                )
            return Response(UserSerializer(user).data, status=status.HTTP_200_OK)

        # 2. Bearer JWT flow
        if auth_header.startswith("Bearer "):
            # тут Django уже раскрутит request.user
            if request.user and request.user.is_authenticated:
                return Response(UserSerializer(request.user).data, status=status.HTTP_200_OK)

            # Если Bearer токен без юзера — ошибка
            return Response({"detail": "Invalid token"}, status=status.HTTP_401_UNAUTHORIZED)

        return Response({"detail": "Unsupported authorization type"},
                        status=status.HTTP_400_BAD_REQUEST)


class RegisterView(APIView):
    """
    POST /api/auth/register/
    - Bearer JWT: регистрация по email, fio, phone, password
    - TMA initData: проверка существующего Telegram-юзера
    """

    def post(self, request):
        auth_header = request.headers.get("Authorization")

        # --- Проверка TMA initData ---
        if auth_header and auth_header.startswith("TMA "):
            init_data = auth_header.split(" ", 1)[1]
            verified = verify_tma(init_data)

            if not verified:
                return Response(
                    {"detail": "Invalid TMA signature"},
                    status=status.HTTP_401_UNAUTHORIZED
                )

            # Достаём данные юзера из initData
            try:
                user_data = json.loads(verified["user"])
                telegram_id = user_data["id"]
            except (KeyError, json.JSONDecodeError):
                return Response(
                    {"detail": "Invalid user data in TMA"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Проверяем, есть ли такой юзер
            user = ProdvizhenieLifeUser.objects.filter(telegram_id=telegram_id).first()
            if user:
                return Response(UserSerializer(user).data, status=status.HTTP_200_OK)
            return Response(
                {"detail": "Пользователь Telegram не найден, зарегистрируйтесь сперва"},
                status=status.HTTP_404_NOT_FOUND
            )

        # --- Bearer регистрация (email+пароль) ---
        if not request.data.get("email") or not request.data.get("password"):
            return Response(
                {"detail": "Email и пароль обязательны"},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = UserCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class UnifiedLoginView(APIView):
    """Логин по email/паролю → ставим токены в куки"""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = UnifiedLoginSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]

        refresh = RefreshToken.for_user(user)
        access, refresh = str(refresh.access_token), str(refresh)

        resp = Response({"detail": "ok", "user": UserSerializer(user).data})
        resp.set_cookie("access", access, httponly=True, secure=True, samesite="Strict", max_age=1800)
        resp.set_cookie("refresh", refresh, httponly=True, secure=True, samesite="Strict", max_age=86400)
        return resp


class RefreshTokenView(APIView):
    """Обновление access токена"""
    def post(self, request):
        refresh = request.COOKIES.get("refresh")
        if not refresh:
            return Response({"detail": "No refresh"}, status=401)
        try:
            token = RefreshToken(refresh)
            access = str(token.access_token)
        except Exception:
            return Response({"detail": "Invalid refresh"}, status=401)

        resp = Response({"detail": "ok"})
        resp.set_cookie("access", access, httponly=True, secure=True, samesite="Strict", max_age=1800)
        return resp


class LogoutView(APIView):
    """Удаляем куки"""
    def post(self, request):
        resp = Response({"detail": "logged out"})
        resp.delete_cookie("access")
        resp.delete_cookie("refresh")
        return resp
