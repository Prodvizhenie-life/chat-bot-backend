from rest_framework import serializers
from .models import Application


class ApplicationSerializer(serializers.ModelSerializer):
    # user_fio = serializers.CharField(source='user.fio', read_only=True)

    class Meta:
        fields = [
            'id',
            'user',
            # 'user_fio',
            'json_data',
            'status',
            'create_at',
            'update_at'
        ]
        read_only_fields = ['id', 'create_at', 'update_at', 'user']


class ApplicationCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = ['json_data', 'status']
