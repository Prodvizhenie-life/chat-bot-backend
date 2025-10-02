Python 3.12

## Подготовка проекта
Скопируйте проект, создайте виртуальное окружение, активируйте его.

### Установка зависимостей 
```python
pip install -r requirements.txt -r requirements-dev.txt
```

### Примените миграции
```python
python manage.py makemigrations
python manage.py migrate
```

### Запустить бота
заполнить .env в соответствии .env_example
```python
python manage.py run_bot
```

### Поднять контейнеры
Заполнить файлы .env в соответствии c .env.example и ./strides/strides/.env.example

В корне проекта:
```python
docker compose up --build -d 
docker compose exec backend python strides/manage.py migrate
docker compose exec backend python strides/manage.py collectstatic --noinput
```