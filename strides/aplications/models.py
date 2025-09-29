from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


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
    is_finished = models.BooleanField(default=False)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
