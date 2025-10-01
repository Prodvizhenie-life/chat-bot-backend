# applications/admin.py
from django.contrib import admin
from .models import Application


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "user",
        "status",
        "create_at",
        "update_at",
    )
    
    list_filter = (
        "status",
        "create_at",
    )
    

    search_fields = (
        "user__email",
        "user__first_name", 
        "user__last_name",
    )
    
    readonly_fields = (
        "create_at",
        "update_at",
    )
    
    fieldsets = (
        ("Основная информация", {
            "fields": ("user", "status")
        }),
        ("JSON данные", {
            "fields": ("json_data",),
            "classes": ("collapse",)
        }),
        ("Даты", {
            "fields": ("create_at", "update_at")
        }),
    )
    
    date_hierarchy = "create_at"
    
    list_per_page = 20

    list_editable = ("status",)