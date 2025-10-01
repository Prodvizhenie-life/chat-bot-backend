import json
import os
import re
from rest_framework import viewsets, status
from rest_framework.response import Response
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
        test_usr = User.objects.first()  # только для разработки
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
            return self._update_draft(
                draft_application,
                request.data,
                request.FILES
            )
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
        if files:
            updated_field = data.get('field') if isinstance(
                data,
                dict
            ) else None
            if updated_field:
                current_json = self.delete_old_files_for_field(
                    current_json,
                    updated_field
                )
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

    def delete_old_files_for_field(self, current_json, field_name):
        """Удаляет старые файлы только для указанного field."""
        if not current_json or not isinstance(current_json, dict):
            return current_json
        if field_name in current_json:
            field_data = current_json[field_name]
            if (
                isinstance(field_data, dict) and
                'file' in field_data and
                isinstance(field_data['file'], list)
            ):
                self._delete_files_for_field(field_name, field_data['file'])
        return current_json

    def _delete_files_for_field(self, field_name, file_urls):
        """Удаляет файлы для конкретного field."""
        if not file_urls:
            return
        safe_field_name = re.sub(r'[^\w\-_]', '_', field_name)
        upload_dir = f'media/uploads/{safe_field_name}/'
        if not os.path.exists(upload_dir):
            return
        deleted_count = 0
        for file_url in file_urls:
            if isinstance(file_url, str):
                filename = os.path.basename(file_url)
                file_path = os.path.join(upload_dir, filename)
                if os.path.exists(file_path) and os.path.isfile(file_path):
                    try:
                        os.remove(file_path)
                        deleted_count += 1
                        print(
                            f"Удален файл: {filename} для field '{field_name}'"
                        )
                    except Exception as e:
                        print(f"Ошибка при удалении {filename}: {e}")

    def _process_images_in_structure(self, json_data, files):
        """Обрабатывает картинки в структуре и преобразует формат."""
        file_urls = {}
        if files:
            field_name = None
            if isinstance(json_data, dict) and 'field' in json_data:
                field_name = json_data['field']
            for file_key, file_obj in files.items():
                file_url = self._save_image(file_obj, field_name)
                file_urls[file_key] = file_url
                print(f"Файл '{file_key}' сохранен: {file_url}")
        result_data = {}
        if isinstance(json_data, dict) and 'field' in json_data:
            doc_id = json_data['field']
        # Создаем чистую структуру без поля field
            doc_structure = {}
            if 'file' in json_data and file_urls:
                file_urls_list = []
                file_keys = json_data['file']
                for key in file_keys:
                    if key in file_urls:
                        file_urls_list.append(file_urls[key])
                doc_structure['file'] = file_urls_list
            
            # Копируем остальные поля кроме 'field'
            for key, value in json_data.items():
                if key not in ['field', 'file']:  # field и file обрабатываем отдельно
                    doc_structure[key] = value
            
            result_data[doc_id] = doc_structure
        
        else:
            result_data = json_data
        
        return result_data

    def _save_image(self, image_data, field_name=None):
        """Сохраняет картинку и возвращает URL файла."""
        print(f"Сохранение файла: {image_data.name} для field: {field_name}")
        if field_name:
            upload_dir = f'media/uploads/{field_name}/'
        else:
            upload_dir = 'media/uploads/unknown/'
        os.makedirs(upload_dir, exist_ok=True)
        import uuid
        file_extension = os.path.splitext(image_data.name)[1]
        filename = f"{uuid.uuid4()}{file_extension}"
        from django.core.files.storage import FileSystemStorage
        fs = FileSystemStorage(location=upload_dir)
        saved_filename = fs.save(filename, image_data)
        if field_name:
            file_url = f"/media/uploads/{field_name}/{saved_filename}"
        else:
            file_url = f"/media/uploads/unknown/{saved_filename}"
        return file_url

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
