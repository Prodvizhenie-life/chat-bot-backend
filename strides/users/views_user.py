from rest_framework import viewsets, permissions, decorators, response, status
from django.db import IntegrityError
from rest_framework.views import APIView

from .models import ProdvizhenieLifeUser
from .serializers import UserSerializer, LinkTelegramSerializer
from .permissions import IsSelfOrAdmin


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления пользователями.

    Endpoints:
    - GET /api/users/ - список пользователей (только админы)
    - GET /api/users/{id}/ - конкретный пользователь (только админы)
    - GET /api/users/me/ - текущий пользователь
    - PATCH /api/users/me/ - обновление своего профиля
    - DELETE /api/users/{id}/ - удаление пользователя (только админы)

    Permissions:
    - list, retrieve, destroy: только администраторы
    - me (GET/PATCH): любой авторизованный пользователь
    """

    queryset = ProdvizhenieLifeUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        """
        Настройка прав доступа в зависимости от действия.

        - Админские операции: list, retrieve, destroy
        - Пользовательские операции: me, update, partial_update
        """
        if self.action in ["list", "retrieve", "destroy"]:
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]

    @decorators.action(detail=False, methods=["get", "patch"], url_path="me")
    def me(self, request):
        """
        Получение и обновление профиля текущего пользователя.

        GET /api/users/me/ - получить свой профиль
        PATCH /api/users/me/ - обновить свой профиль (частично)

        Returns:
            200: Данные пользователя
            400: Ошибка валидации (при PATCH)
        """
        if request.method == "GET":
            serializer = self.get_serializer(request.user)
            return response.Response(serializer.data)

        elif request.method == "PATCH":
            serializer = self.get_serializer(
                request.user,
                data=request.data,
                partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return response.Response(serializer.data)


class LinkTelegramView(APIView):
    """
    Привязка Telegram аккаунта к текущему пользователю.

    POST /api/link-telegram/
    Body: { "telegram_id": 123456789 }

    Требования:
    - Пользователь авторизован
    - У пользователя ещё нет привязанного Telegram
    - Указанный telegram_id не используется другим пользователем

    Returns:
        200: Telegram успешно привязан
        400: Ошибка валидации или telegram_id уже занят
        401: Пользователь не авторизован
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """Обработка запроса на привязку Telegram."""
        serializer = LinkTelegramSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)

        telegram_id = serializer.validated_data['telegram_id']

        try:
            request.user.telegram_id = telegram_id
            request.user.save(update_fields=['telegram_id'])
        except IntegrityError:
            # На случай race condition — кто-то успел привязать этот ID
            return response.Response(
                {"detail": "Этот Telegram аккаунт уже занят"},
                status=status.HTTP_400_BAD_REQUEST
            )

        return response.Response(
            {"detail": "Telegram аккаунт успешно привязан"},
            status=status.HTTP_200_OK
        )


class UnlinkTelegramView(APIView):
    """
    Отвязка Telegram аккаунта от текущего пользователя.

    POST /api/unlink-telegram/

    Требования:
    - Пользователь авторизован
    - У пользователя есть привязанный Telegram

    После отвязки пользователь сможет:
    - Привязать другой Telegram аккаунт
    - Продолжить использовать систему через email/password

    Returns:
        200: Telegram успешно отвязан
        400: У пользователя нет привязанного Telegram
        401: Пользователь не авторизован
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """Обработка запроса на отвязку Telegram."""
        if not request.user.telegram_id:
            return response.Response(
                {"detail": "У вас нет привязанного Telegram аккаунта"},
                status=status.HTTP_400_BAD_REQUEST
            )

        request.user.telegram_id = None
        request.user.save(update_fields=['telegram_id'])

        return response.Response(
            {"detail": "Telegram аккаунт успешно отвязан"},
            status=status.HTTP_200_OK
        )
