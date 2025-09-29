from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Application, ApplicationStatus
from .serializers import (
    ApplicationSerializer,
    ApplicationCreateUpdateSerializer
)


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
        - Для создания/обновления: ApplicationCreateUpdateSerializer (только нужные поля)
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
        current_json = draft_application.json_data or {}
        if 'json_data' in data and data['json_data']:
            new_json_data = data['json_data']
            merged_json = self._deep_merge(current_json, new_json_data)
            data['json_data'] = merged_json
        serializer = self.get_serializer(
            draft_application,
            data=data,
            partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def _deep_merge(self, original, new):
        """Рекурсивно оъединяет и сохраняет json"""
        result = original.copy()
        for key, value in new.items():
            if key == 'image' and value:
                result[key] = self._save_image(value)
            elif (
                key in result and isinstance(result[key], dict) and
                isinstance(value, dict)
            ):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        return result
    
    def _save_image(image):
        """Сохраняет картинки"""
        ...

    def _create_new_application(self, data):
        """Создает новую заявку."""
        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            serializer.save(user=self.request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
