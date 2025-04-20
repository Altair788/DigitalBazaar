from django.contrib import admin

from reviews.models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("text", "author", "ad", "created_at")
    ordering = (
        "id",
        "-created_at",
    )
