# # apps/requests/admin.py
# from django.contrib import admin
# from .models import Aplication


# @admin.register(Aplication)
# class ApplicationAdmin(admin.ModelAdmin):
#     list_display = (
#         "subject_full_name",
#         "applicant_type",
#         "status",
#         "created_at",
#         "submitted_at",
#     )
#     list_filter = ("status", "applicant_type", "created_at")
#     search_fields = ("subject_full_name", "contact_email", "contact_phone")
#     readonly_fields = ("created_at", "updated_at", "submitted_at")
