from django.contrib.auth.models import AbstractUser
from django.db import models


class UserRole(models.TextChoices):
    APPLICANT = 'applicant', 'Applicant'
    MODERATOR = 'moderator', 'Moderator'
    ADMIN = 'admin', 'Admin'


class User(AbstractUser):
    """
    Кастомный пользователь.
    Наследуем AbstractUser (username/email/password уже есть).
    Добавляем full_name и роль.
    """
    full_name = models.CharField(max_length=255, blank=True)
    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.APPLICANT,
    )


    def __str__(self):
        return self.full_name or self.username
