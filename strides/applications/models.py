from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class ApplicationStatus(models.TextChoices):
    DRAFT = 'draft', 'Черновик'
    SUBMITTED = 'submitted', 'Отправлена'
    REVIEW = 'review', 'Необходима проверка'
    APPROVED = 'approved', 'Одобрена'
    REJECTED = 'rejected', 'Отклонена'
    ARCHIVED = 'archived', 'В архиве'


class QuestionType(models.TextChoices):
    TEXT = 'text', 'Текст'
    BOOLEAN = 'boolean', 'Да/Нет'
    DOCUMENT = 'document', 'Документ'
    MULTIPLE_CHOICE = 'multiple_choice', 'Множественный выбор'
    DATE = 'date', 'Дата'
    NUMBER = 'number', 'Число'


class AnswerCategory(models.TextChoices):
    GENERAL = 'general', 'Общая информация'
    DETAILED = 'detailed', 'Подробная информация'
    DOCUMENTS = 'documents', 'Документы'


class Application(models.Model):
    """
    Заявки пользователя.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='applications'
    )
    status = models.CharField(
        max_length=20,
        choices=ApplicationStatus.choices,
        default=ApplicationStatus.DRAFT,
        db_index=True,
    )
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        """Строковое представление заявки."""
        user_email = self.user.email if self.user and self.user.email else "Аноним"
        return f"Заявка #{self.id} - {user_email} - {self.get_status_display()}"

    class Meta:
        verbose_name = "Заявка"
        verbose_name_plural = "Заявки"
        ordering = ['-create_at']


class Answer(models.Model):
    """
    Ответы на вопросы в заявках.
    """
    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name='answers',
        verbose_name='Заявка'
    )
    question_field = models.CharField(
        max_length=100,
        verbose_name='Поле вопроса',
        help_text='Идентификатор поля вопроса (например, "fio", "passport_photo")'
    )
    question_type = models.CharField(
        max_length=20,
        choices=QuestionType.choices,
        verbose_name='Тип вопроса',
        db_index=True
    )
    value = models.JSONField(
        blank=True,
        null=True,
        verbose_name='Значение поля'
    )
    category = models.CharField(
        max_length=20,
        choices=AnswerCategory.choices,
        verbose_name='Категория',
        db_index=True
    )
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Ответ'
        verbose_name_plural = 'Ответы'
        unique_together = ['application', 'id']
        indexes = [
            models.Index(fields=['application', 'question_field']),
            models.Index(fields=['category', 'question_type']),
        ]

    def __str__(self):
        return f"Ответ #{self.id} - {self.question_field} - {self.application_id}"
