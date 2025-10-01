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