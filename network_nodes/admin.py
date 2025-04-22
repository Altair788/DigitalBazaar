from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from network_nodes.models import NetworkNode


@admin.register(NetworkNode)
class NetworkNodeAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "node_type",
        "email",
        "country",
        "city",
        "supplier_link",
        "debt_to_supplier",
        "created_at",
        "level",
    )
    list_filter = ("city",)
    search_fields = ("name", "city", "country")
    ordering = ("id", "-created_at")
    readonly_fields = ("created_at", "level", "supplier_link")

    @admin.display(description="Поставщик")
    def supplier_link(self, obj):
        if obj.supplier:
            url = reverse(
                "admin:{}_{}_change".format(
                    obj.supplier._meta.app_label, obj.supplier._meta.model_name
                ),
                args=[obj.supplier.id],
            )
            return format_html('<a href="{}">{}</a>', url, obj.supplier.name)
        return "-"

    # Admin action для обнуления задолженности
    @admin.action(description="Очистить задолженность перед поставщиком")
    def clear_debt(self, request, queryset):
        updated = queryset.update(debt_to_supplier=0)
        self.message_user(request, f"Задолженность очищена у {updated} объектов.")

    actions = [clear_debt]
