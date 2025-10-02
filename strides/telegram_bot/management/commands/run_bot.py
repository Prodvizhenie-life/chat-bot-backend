from django.core.management.base import BaseCommand
from django.conf import settings
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    WebAppInfo
)
from telegram.ext import Application, CommandHandler


class Command(BaseCommand):
    help = 'Запускает простого Telegram бота с одной кнопкой'

    def handle(self, *args, **options):
        token = getattr(settings, 'TELEGRAM_BOT_TOKEN', None)
        if not token:
            self.stderr.write(
                'Ошибка: TELEGRAM_BOT_TOKEN не найден в настройках'
            )
            return

        application = Application.builder().token(token).build()

        async def start_command(update: Update, context):
            user = update.effective_user
            keyboard = [[
                InlineKeyboardButton(
                    text="Открыть приложение",
                    web_app=WebAppInfo(url=settings.FRONTEND_URL)
                )
            ]]
            await update.message.reply_text(
                f"Привет, {user.first_name}!\n"
                "Нажми кнопку чтобы открыть приложение:",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        application.add_handler(CommandHandler("start", start_command))
        self.stdout.write('Бот запущен!')
        application.run_polling()
