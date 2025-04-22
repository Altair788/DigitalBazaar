from rest_framework import permissions

class CanViewAPI(permissions.BasePermission):
    """
    Разрешение для просмотра API только активным сотрудникам.
    """
    # комментарий к статусу is_active - user становится активным при подтверждении email
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_staff)


#
# class IsAdmin(permissions.BasePermission):
#     """
#     Проверяет, является ли пользователь администратором.
#     """
#
#     def has_permission(self, request, view):
#         return request.user.groups.filter(name="admins").exists()
#
#
# class IsAuthor(permissions.BasePermission):
#     """
#     Проверяет, является ли пользователь владельцем.
#     """
#
#     def has_object_permission(self, request, view, obj):
#         if obj.author == request.user:
#             return True
#         return False
