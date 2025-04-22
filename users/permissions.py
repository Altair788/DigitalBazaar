from rest_framework import permissions

# users/permissions.py
# предполагается, что регистрируются в сервисе сотрудники компании
# (активными сотрудниками они становятся при подтверждении почты) Аутентификация проходит по email
class IsActiveEmployee(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_active



class IsAdmin(permissions.BasePermission):
    """
    Проверяет, является ли пользователь администратором.
    """

    def has_permission(self, request, view):
        return request.user.groups.filter(name="admins").exists()
