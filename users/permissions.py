from rest_framework import permissions

# users/permissions.py
class IsActiveEmployee(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_active and request.user.is_staff



class IsAdmin(permissions.BasePermission):
    """
    Проверяет, является ли пользователь администратором.
    """

    def has_permission(self, request, view):
        return request.user.groups.filter(name="admins").exists()
