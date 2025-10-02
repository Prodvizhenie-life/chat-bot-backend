from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views_auth import (
    UnifiedLoginView,
    RefreshTokenView,
    LogoutView,
    InitView,
    RegisterView
)
from .views_user import (
    UserViewSet,
    LinkTelegramView,
    UnlinkTelegramView
)

router = DefaultRouter()
router.register("users", UserViewSet, basename="user")

urlpatterns = [
    path("init/", InitView.as_view(), name="tma-init"),
    path("register/", RegisterView.as_view(), name="tma-register"),
    path("login/", UnifiedLoginView.as_view(), name="unified-login"),
    path("refresh/", RefreshTokenView.as_view(), name="refresh"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("link-telegram/", LinkTelegramView.as_view(), name="link-telegram"),
    path("unlink-telegram/", UnlinkTelegramView.as_view(), name="unlink-telegram"),
    path("", include(router.urls)),
]
