from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Application, ApplicationStatus
from .serializers import ApplicationSerializer, ApplicationCreateUpdateSerializer


class ApplicationViewSet(viewsets.ModelViewSet):
    """
    ViewSet для работы с заявками пользователя.
    Предоставляет CRUD операции и кастомные actions.
    """
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Возвращает только заявки текущего пользователя."""
        return Application.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        """
        Выбираем сериализатор в зависимости от действия.
        - Для создания/обновления: AplicationCreateUpdateSerializer (только нужные поля)
        - Для остального: AplicationSerializer (все поля + read_only)
        """
        if self.action in ['create', 'update', 'partial_update']:
            return ApplicationCreateUpdateSerializer
        return ApplicationSerializer

    def perform_create(self, serializer):
        """
        Автоматически привязывает заявку к текущему пользователю при создании.
        """
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        draft_aplication = Application.objects.filter(
            user=self.request.user,
            status=ApplicationStatus.DRAFT
        ).first()
        if draft_aplication:
            return self._update_draft(draft_aplication, request.data)
        return self._create_new_application(request.data)

    def _update_draft(self, draft_application, data):
        """Обновляет существующий черновик."""
        ...

    def _create_new_application(self, data):
        """Создает новую заявку."""
        ...
