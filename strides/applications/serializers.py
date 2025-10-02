from rest_framework import serializers
from .models import Application, Answer


class AnswerSerializer(serializers.ModelSerializer):
    """Сериализатор для ответов с валидацией."""
    
    class Meta:
        model = Answer
        fields = [
            'id',
            'question_field',
            'question_type', 
            'value',
            'category',
            'create_at',
            'update_at'
        ]
        read_only_fields = ['id', 'create_at', 'update_at']

    def validate(self, attrs):
        """Валидация всех полей."""
        required_fields = ['question_field', 'question_type', 'value', 'category']
        for field in required_fields:
            if field not in attrs:
                raise serializers.ValidationError({field: 'Это поле обязательно'})
        return attrs


class ApplicationSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения заявки с ответами."""
    answers = AnswerSerializer(many=True, read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = Application
        fields = [
            'id',
            'user',
            'user_email',
            'status', 
            'answers',
            'create_at',
            'update_at'
        ]
        read_only_fields = ['id', 'user', 'create_at', 'update_at']


class ApplicationCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания заявки."""

    class Meta:
        model = Application
        fields = ['id', 'status']
        read_only_fields = ['id']


class ApplicationUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для обновления заявки."""

    class Meta:
        model = Application
        fields = ['status']