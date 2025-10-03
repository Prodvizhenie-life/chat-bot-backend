
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Application, Answer


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 0
    readonly_fields = (
        'question_field', 'question_type',
        'simple_display_value', 'category', 'answer_link'
    )
    fields = (
        'answer_link', 'question_field',
        'question_type', 'simple_display_value', 'category'
    )

    def simple_display_value(self, obj):
        if obj.value is None:
            return "-"
        if obj.question_type == 'document' and isinstance(obj.value, list):
            links = []
            for file_path in obj.value:
                if file_path.startswith('/media/'):
                    file_url = file_path
                else:
                    file_url = f"/media/{file_path.lstrip('/')}"
                file_name = file_path.split('/')[-1]
                links.append(
                    f'<a href="{file_url}" target="_blank">{file_name}</a>'
                )
            return format_html('<br>'.join(links))
        return str(obj.value)
    simple_display_value.short_description = 'Значение'

    def answer_link(self, obj):
        if obj.id:
            url = reverse('admin:applications_answer_change', args=[obj.id])
            return format_html('<a href="{}">Перейти к вопросу</a>', url)
        return "-"
    answer_link.short_description = ''


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('id_formatted', 'user_info', 'status', 'create_at')
    list_display_links = ('id_formatted',)
    list_filter = ('status', 'create_at')
    search_fields = ('user__email', 'user__fio', 'user__phone', 'id')
    readonly_fields = ('create_at', 'update_at')
    list_editable = ("status",)
    inlines = [AnswerInline]

    def id_formatted(self, obj):
        return f'Заявка №{obj.id}'
    id_formatted.short_description = 'ID'

    def user_info(self, obj):
        user = obj.user
        if user:
            return f"{user.fio} ({user.email})"
        return "Нет пользователя"
    user_info.short_description = 'Пользователь'


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'application', 'user_fio',
        'file_display', 'question_type', 'category'
    )
    list_filter = ('question_type', 'category')
    search_fields = ('user_fio',)
    readonly_fields = ('create_at', 'update_at', 'file_display')

    def user_fio(self, obj):
        return obj.application.user.fio if obj.application.user else "-"
    user_fio.short_description = 'ФИО пользователя'

    def file_display(self, obj):
        if obj.question_type == 'document' and isinstance(obj.value, list):
            links = []
            for file_path in obj.value:
                if file_path.startswith('/media/'):
                    file_url = file_path
                else:
                    file_url = f"/media/{file_path.lstrip('/')}"
                file_name = file_path.split('/')[-1]
                links.append(
                    f'<a href="{file_url}" target="_blank">{file_name}</a>'
                )
            return format_html('<br>'.join(links))
        return str(obj.value)
    file_display.short_description = 'Содержимое ответа'
