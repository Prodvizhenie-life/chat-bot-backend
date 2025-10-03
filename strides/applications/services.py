import os
import uuid
import re
from django.conf import settings


class FileStorageService:

    def save_doc(self, image_data, field_name=None):
        """Сохраняет изображение и возвращает URL."""
        safe_field_name = self._get_safe_field_name(field_name)
        upload_dir = os.path.join(
            settings.MEDIA_ROOT,
            'uploads',
            safe_field_name
        )
        os.makedirs(upload_dir, exist_ok=True)
        file_extension = os.path.splitext(image_data.name)[1]
        filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(upload_dir, filename)
        with open(file_path, 'wb') as f:
            for chunk in image_data.chunks():
                f.write(chunk)
        return f"{settings.MEDIA_URL}uploads/{safe_field_name}/{filename}"

    @staticmethod
    def delete_file_by_url(file_url):
        """Удаляет файл по URL."""
        try:
            if file_url.startswith(settings.MEDIA_URL):
                relative_path = file_url[len(settings.MEDIA_URL):]
                file_path = os.path.join(settings.MEDIA_ROOT, relative_path)
                if os.path.exists(file_path):
                    os.remove(file_path)
                    print(f"Удален файл: {file_path}")
        except Exception as e:
            print(f"Ошибка при удалении файла: {e}")

    @staticmethod
    def _get_safe_field_name(field_name):
        """Возвращает безопасное имя для использования в путях."""
        if not field_name:
            return 'unknown'
        return re.sub(r'[^\w\-_]', '_', field_name)


file_storage = FileStorageService()
