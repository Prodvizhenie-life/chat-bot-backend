import json
import os
import re
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Application, ApplicationStatus, Answer, AnswerCategory, QuestionType
from .serializers import (
    ApplicationSerializer,
    ApplicationCreateSerializer,
    ApplicationUpdateSerializer,
    AnswerSerializer
)
from .services import file_storage
from django.contrib.auth import get_user_model

User = get_user_model()


class ApplicationViewSet(viewsets.ModelViewSet):
    """
    ViewSet для работы с заявками пользователя.
    Предоставляет CRUD операции и кастомные actions.
    """
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'put', 'patch', 'head', 'options']

    def get_queryset(self):
        """Возвращает только заявки текущего пользователя."""
        return Application.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        """
        Выбираем сериализатор в зависимости от действия.
        - Для создания: ApplicationCreateSerializer
        - Для обновления: ApplicationUpdateSerializer 
        - Для чтения: ApplicationSerializer (все поля + ответы)
        """
        if self.action == 'create':
            return ApplicationCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return ApplicationUpdateSerializer
        return ApplicationSerializer

    def perform_create(self, serializer):
        """
        Создает пустую заявку.
        """
        serializer.save(
            user=self.request.user,
            status=ApplicationStatus.DRAFT
            )

    def create(self, request, *args, **kwargs):
        draft_application = Application.objects.filter(
            user=self.request.user,
            status=ApplicationStatus.DRAFT
        ).first()
        if draft_application:
            serializer = ApplicationSerializer(draft_application)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return super().create(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        """Обработка PATCH запросов - обновление одного ответа заявки"""
        instance = self.get_object()
        question_data = {}
        if 'question' in request.data:
            question_data = request.data['question']
            if isinstance(question_data, str):
                try:
                    question_data = json.loads(question_data)
                except (json.JSONDecodeError, TypeError):
                    return Response(
                        {'error': 'Invalid JSON in question field'}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
            serializer = AnswerSerializer(data=question_data)
            serializer.is_valid(raise_exception=True)
            validated_question_data = serializer.validated_data
            if request.FILES:
                validated_question_data = self._process_files(validated_question_data, request.FILES)
            self._save_answer(instance, validated_question_data)
        if 'status' in request.data:
            instance.status = request.data['status']
            instance.save()
        response_serializer = ApplicationSerializer(instance)
        return Response(response_serializer.data, status=status.HTTP_200_OK)

    def _process_files(self, answer_data, files):
        """Обрабатывает файлы и возвращает обновленные данные ответа."""
        processed_data = answer_data.copy()
        file_urls = []
        field_name = answer_data.get('question_field')
        for _, file_obj in files.items():
            file_url = file_storage.save_doc(file_obj, field_name)
            file_urls.append(file_url)
        if file_urls:
            processed_data['value'] = file_urls
            processed_data['question_type'] = QuestionType.DOCUMENT
            processed_data['category'] = AnswerCategory.DOCUMENTS
        return processed_data

    def _save_answer(self, application, answer_data):
        """Сохраняет или обновляет один ответ."""
        question_field = answer_data['question_field']
        question_type = answer_data['question_type']
        value = answer_data['value']
        category = answer_data['category']
        self._delete_old_files_from_database(application, question_field)
        Answer.objects.update_or_create(
            application=application,
            question_field=question_field,
            defaults={
                'question_type': question_type,
                'value': value,
                'category': category
            }
        )

    def _delete_old_files_from_database(self, application, field_name):
        """Удаляет старые файлы из существующего ответа в базе."""
        try:
            old_answer = Answer.objects.get(
                application=application, 
                question_field=field_name
            )
            if old_answer.value and isinstance(old_answer.value, list):
                for file_url in old_answer.value:
                    file_storage.delete_file_by_url(file_url)
                    print(f"Удален старый файл: {file_url}")
        except Answer.DoesNotExist:
            pass
