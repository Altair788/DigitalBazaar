# from django.contrib import admin
#
# from users.models import User
#
# admin.site.register(User)


from django.contrib import admin

from users.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "email",
        "first_name",
        "last_name",
        "tg_nick",
        "tg_id",
        "role",
        "is_staff",
        "is_active",
        "is_superuser",
    )
    ordering = ("id",)
