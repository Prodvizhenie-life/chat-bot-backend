from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class UserRole(models.TextChoices):
    APPLICANT = 'applicant', 'Applicant'
    MODERATOR = 'moderator', 'Moderator'
    ADMIN = 'admin', 'Admin'


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, fio=None, **extra_fields):
        if not email:
            raise ValueError("Email обязателен")
        email = self.normalize_email(email)
        user = self.model(email=email, fio=fio, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, fio="Admin", **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", UserRole.ADMIN)
        return self.create_user(email, password, fio=fio, **extra_fields)


class ProdvizhenieLifeUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    fio = models.CharField(max_length=255)
    phone = models.CharField(max_length=20, unique=True)

    # Telegram fields
    telegram_id = models.BigIntegerField(blank=True, null=True, unique=True)
    access_hash = models.CharField(max_length=128, blank=True, null=True)
    first_name = models.CharField(max_length=150, blank=True, null=True)
    last_name = models.CharField(max_length=150, blank=True, null=True)
    username = models.CharField(max_length=150, blank=True, null=True)
    photo = models.URLField(blank=True, null=True)
    language_code = models.CharField(max_length=10, blank=True, null=True)

    # Служебные флаги
    is_auth_tg = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    # Роль
    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.APPLICANT,
    )

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["fio"]

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return f"{self.email} ({self.role})"
