from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AplicationViewSet

router = DefaultRouter()
router.register('aplications', AplicationViewSet, basename='aplications')

urlpatterns = [
    path('', include(router.urls)),
]