from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from .models import ProdvizhenieLifeUser


@admin.register(ProdvizhenieLifeUser)
class UserAdmin(DjangoUserAdmin):
    model = ProdvizhenieLifeUser
    list_display = ("username", "fio", "email", "role", "is_staff", "is_superuser")
    fieldsets = DjangoUserAdmin.fieldsets + (
        (None, {"fields": ("fio", "role")}),
    )
