import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone


class ApplicantType(models.TextChoices):
    SELF = 'self', 'Я и есть подопечный'
    PARENT = 'parent', 'Мать/отец'
    GUARDIAN = 'guardian', 'Опекун'
    RELATIVE = 'relative', 'Родственник'


class ApplicationStatus(models.TextChoices):
    DRAFT = 'draft', 'Черновик'
    SUBMITTED = 'submitted', 'Отправлена'
    REVIEW = 'review', 'Необходима проверка'
    APPROVED = 'approved', 'Одобрена'
    REJECTED = 'rejected', 'Отклонена'


class Application(models.Model):
    """
    Минимальная модель заявки (ключевые поля).
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="applications"
    )

    applicant_type = models.CharField(
        max_length=16,
        choices=ApplicantType.choices,
        default=ApplicantType.SELF,
    )

    # Данные подопечного
    subject_full_name = models.CharField("ФИО подопечного", max_length=255)
    subject_dob = models.DateField("Дата рождения подопечного", null=True, blank=True)

    # Контакты
    contact_phone = models.CharField("Телефон", max_length=40, blank=True)
    contact_email = models.EmailField("Email", blank=True)

    # Статус
    status = models.CharField(
        max_length=20,
        choices=ApplicationStatus.choices,
        default=ApplicationStatus.DRAFT,
        db_index=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    submitted_at = models.DateTimeField(null=True, blank=True)

    def submit(self):
        self.status = ApplicationStatus.SUBMITTED
        self.submitted_at = timezone.now()
        self.save(update_fields=["status", "submitted_at", "updated_at"])

    def __str__(self):
        return f"{self.subject_full_name} ({self.id})"
