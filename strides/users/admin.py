from django.contrib import admin
from .models import ProdvizhenieLifeUser, UserRole
from applications.models import Application, ApplicationStatus


@admin.register(ProdvizhenieLifeUser)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        "email",
        "fio",
        "phone",
        "role",
        "is_active",
        "is_staff",
        "draft_info",
        "submitted_info",
        "review_info",
        "approved_info",
        "rejected_info",
    )

    search_fields = ("email", "fio", "phone")
    list_filter = ("role", "is_active", "is_staff")

    def _status_info(self, obj, status):
        qs = obj.applications.filter(status=status)
        count = qs.count()
        last_date = qs.order_by("-update_at").values_list("update_at", flat=True).first()
        if last_date:
            return f"{count} ({last_date:%Y-%m-%d})"
        return str(count)

    def draft_info(self, obj):
        return self._status_info(obj, ApplicationStatus.DRAFT)
    draft_info.short_description = "Черновики"

    def submitted_info(self, obj):
        return self._status_info(obj, ApplicationStatus.SUBMITTED)
    submitted_info.short_description = "Отправлено"

    def review_info(self, obj):
        return self._status_info(obj, ApplicationStatus.REVIEW)
    review_info.short_description = "На проверке"

    def approved_info(self, obj):
        return self._status_info(obj, ApplicationStatus.APPROVED)
    approved_info.short_description = "Одобрено"

    def rejected_info(self, obj):
        return self._status_info(obj, ApplicationStatus.REJECTED)
    rejected_info.short_description = "Отклонено"
