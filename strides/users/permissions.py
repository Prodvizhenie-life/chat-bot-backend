from rest_framework import permissions


class IsSelfOrAdmin(permissions.BasePermission):
    """
    Доступ разрешён:
    - самому пользователю (на чтение/изменение своего профиля)
    - администратору (на всё)
    """

    def has_object_permission(self, request, view, obj):
        return (
            obj == request.user  # свой профиль
            or request.user.is_superuser
            or request.user.role == "admin"
        )
