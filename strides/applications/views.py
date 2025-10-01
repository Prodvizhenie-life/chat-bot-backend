import json
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Application, ApplicationStatus
from .serializers import (
    ApplicationSerializer,
    ApplicationCreateUpdateSerializer
)

from django.contrib.auth import get_user_model

User = get_user_model()

class ApplicationViewSet(viewsets.ModelViewSet):
    """
    ViewSet для работы с заявками пользователя.
    Предоставляет CRUD операции и кастомные actions.
    """
    # permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Возвращает только заявки текущего пользователя."""
        # return Application.objects.filter(user=self.request.user)
        return Application.objects.filter(user=User.objects.first()) # только для разработки

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
        test_usr=User.objects.first()
        serializer.save(
            user=test_usr,  # только для разработки
            # user=self.request.user,
            json_data={},
            status=ApplicationStatus.DRAFT
            )

    def create(self, request, *args, **kwargs):
        draft_application = Application.objects.filter(
            user=User.objects.first(),  # только для разработки
            # user=self.request.user,
            status=ApplicationStatus.DRAFT
        ).first()
        if draft_application:
            return self._update_draft(draft_application, request.data, request.FILES)
        return self._create_new_application(request.data)

    def partial_update(self, request, *args, **kwargs):
        """Обработка PATCH запросов - обновление существующей заявки"""
        instance = self.get_object()
        print(f'request.data:{request.data}')
        print(f'request.FILES:{request.FILES}')
        if request.FILES:
            json_data_str = request.data.get('json_data', '{}')
            try:
                json_data = json.loads(json_data_str)
            except json.JSONDecodeError:
                json_data = {}
            return self._update_draft(instance, json_data, request.FILES)
        else:
            return self._update_draft(instance, request.data)

    def _update_draft(self, draft_application, data, files=None):
        """Обновляет существующий черновик."""
        current_json = draft_application.json_data or {}
        processed_json = self._process_images_in_structure(data, files)
        merged_json = {**current_json, **processed_json}
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

    def _process_images_in_structure(self, json_data, files):
        """🔧 ЗАГЛУШКА: Обрабатывает картинки в структуре."""
        print("Заглушка: Обработка картинок в структуре")
        # Пока просто возвращаем данные как есть
        return json_data

    def _save_image(self, image_data):
        """🔧 ЗАГЛУШКА: Сохраняет картинки."""
        print("Заглушка: Сохранение картинки")
        return image_data  # временно возвращаем как есть

    def _create_new_application(self, data):
        """Создает новую заявку."""
        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            test_usr = User.objects.first()  # только для разработки
            serializer.save(
                user=test_usr,
                json_data={},
                status=ApplicationStatus.DRAFT
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)