from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class ApplicationStatus(models.TextChoices):
    DRAFT = 'draft', 'Черновик'
    SUBMITTED = 'submitted', 'Отправлена'
    REVIEW = 'review', 'Необходима проверка'
    APPROVED = 'approved', 'Одобрена'
    REJECTED = 'rejected', 'Отклонена'


class Aplication(models.Model):
    """
    Заявки пользователя.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='aplications'
    )
    json_data = models.JSONField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=ApplicationStatus.choices,
        default=ApplicationStatus.DRAFT,
        db_index=True,
    )
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
