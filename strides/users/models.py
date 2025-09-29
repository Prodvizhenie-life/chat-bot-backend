from django.contrib.auth.models import AbstractUser
from django.db import models


class UserRole(models.TextChoices):
    APPLICANT = 'applicant', 'Applicant'
    MODERATOR = 'moderator', 'Moderator'
    ADMIN = 'admin', 'Admin'


class ProdvizhenieLifeUser(AbstractUser):
    """
    Кастомный пользователь.
    Наследуем AbstractUser (username/email/password уже есть).
    Добавляем full_name и роль.
    """
    telegram_id = models.BigIntegerField(
        unique=True,
        null=True,
        blank=True,
    )
    first_name = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )
    fio = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )
    language_code = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )
    photo_url = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )
    email_is_confirm = models.BooleanField(default=False)
    phone = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )
    phone_is_confirm = models.BooleanField(default=False)
    is_auth_tg = models.BooleanField(default=False)
    company_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )
    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.APPLICANT,
    )

    def __str__(self):
        return self.fio
