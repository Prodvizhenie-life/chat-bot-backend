from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class ApplicationStatus(models.TextChoices):
    DRAFT = 'draft', 'Черновик'
    SUBMITTED = 'submitted', 'Отправлена'
    REVIEW = 'review', 'Необходима проверка'
    APPROVED = 'approved', 'Одобрена'
    REJECTED = 'rejected', 'Отклонена'


class Application(models.Model):
    """
    Заявки пользователя.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='applications'
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

    def __str__(self):
        """Строковое представление заявки."""
        user_email = self.user.email if self.user and self.user.email else "Аноним"
        return f"Заявка #{self.id} - {user_email} - {self.get_status_display()}"

    class Meta:
        verbose_name = "Заявка"
        verbose_name_plural = "Заявки"
        ordering = ['-create_at']
