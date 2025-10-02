from rest_framework import viewsets, permissions, decorators, response, status
from django.db import IntegrityError
from rest_framework.views import APIView

from .models import ProdvizhenieLifeUser
from .serializers import UserSerializer, LinkTelegramSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = ProdvizhenieLifeUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.action in ["list", "retrieve", "destroy"]:
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]

    @decorators.action(detail=False, methods=["get", "patch"], url_path="me")
    def me(self, request):
        if request.method == "GET":
            return response.Response(self.get_serializer(request.user).data)
        elif request.method == "PATCH":
            serializer = self.get_serializer(request.user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return response.Response(serializer.data)

class LinkTelegramView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = LinkTelegramSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        telegram_id = serializer.validated_data['telegram_id']
        try:
            request.user.telegram_id = telegram_id
            request.user.save(update_fields=['telegram_id'])
        except IntegrityError:
            return response.Response({"detail": "Этот Telegram уже занят"}, status=400)
        return response.Response({"detail": "Telegram привязан"})

class UnlinkTelegramView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        if not request.user.telegram_id:
            return response.Response({"detail": "У вас нет привязанного Telegram"}, status=400)
        request.user.telegram_id = None
        request.user.save(update_fields=['telegram_id'])
        return response.Response({"detail": "Telegram отвязан"})
