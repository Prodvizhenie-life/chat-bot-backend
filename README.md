Python 3.12

# Django Backend API: Фонд «Продвижение»

Это бэкенд API для Telegram Mini App и веб-виджета фонда «Продвижение».

Приложение обеспечивает:
- Гибридную авторизацию (Telegram Mini Apps + Email/Password)
- Управление пользователями и заявками
- REST API для фронтенда
- Административную панель Django

---

## 🚀 Быстро посмотреть


- **API Documentation**: `https://back.prodvizhenie.tw1.ru/api/swagger/` Swagger

**Основные эндпоинты:**
- `POST /api/auth/register/` - регистрация (email или Telegram)
- `POST /api/auth/login/` - вход в систему
- `GET /api/applications/` - список заявок

---

## 🛠 Используемые технологии

**Core:**
- [Django 5.0.6](https://www.djangoproject.com/) - веб-фреймворк
- [Django REST Framework](https://www.django-rest-framework.org/) - REST API
- [PostgreSQL](https://www.postgresql.org/) - основная БД

**Авторизация:**
- [SimpleJWT](https://django-rest-framework-simplejwt.readthedocs.io/) - JWT токены
- [aiogram](https://docs.aiogram.dev/) - валидация Telegram Mini Apps
- [Djoser](https://djoser.readthedocs.io/) - управление пользователями

**Production:**
- [Gunicorn](https://gunicorn.org/) - WSGI сервер
- [Nginx](https://nginx.org/) - reverse proxy
- [Docker](https://www.docker.com/) - контейнеризация

---

## 🚀 Как запустить локально


### Вариант с Docker (рекомендуемый)

Проект полностью готов к развёртыванию в контейнерах.

1. **Настройте `.env` файл:**
    ```bash
    cp .env.example .env
    # Отредактируйте значения
    ```

2. **Запустите всё одной командой:**
    ```bash
    docker-compose up --build -d
    ```

3. **Примените миграции:**
    ```bash
    docker-compose exec web python manage.py migrate
    ```

4. **Создайте суперпользователя:**
    ```bash
    docker-compose exec web python manage.py createsuperuser
    ```

5. **Проверьте логи:**
    ```bash
    docker-compose logs -f web
    ```

---

## 🐳 Docker Compose

### Основные команды:

```bash
# Запустить всё
docker-compose up -d

# Остановить
docker-compose down

# Пересобрать образы
docker-compose up --build

# Логи
docker-compose logs -f web

# Выполнить команду в контейнере
docker-compose exec web python manage.py shell

# Зайти внутрь контейнера
docker-compose exec web bash
```
---
