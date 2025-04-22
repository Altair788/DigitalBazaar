from rest_framework import serializers

from network_nodes.models import NetworkNode, Product
from network_nodes.validators import NetworkNodeValidator


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["id", "name", "model", "release_date"]

class NetworkNodeSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели NetworkNode.
    """
    products = ProductSerializer(
        many=True,
        read_only=True
    )

    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(
        required=True,
        error_messages={"required": "Название звена сети обязательно."}
    )
    node_type = serializers.ChoiceField(
        choices=NetworkNode.NODE_TYPE_CHOICES,
        required=True,
        error_messages={"required": "Тип звена обязателен для заполнения."}
    )
    email = serializers.EmailField(
        required=True,
        error_messages={"required": "Электронная почта обязательна для заполнения."}
    )
    phone = serializers.CharField(
        allow_null=True,
        required=False,
        help_text="Укажите телефон"
    )
    country = serializers.CharField(
        required=True,
        error_messages={"required": "Страна обязательна для заполнения."}
    )
    city = serializers.CharField(
        required=True,
        error_messages={"required": "Город обязателен для заполнения."}
    )
    street = serializers.CharField(
        allow_null=True,
        required=False,
        help_text="Укажите улицу"
    )
    house_number = serializers.CharField(
        required=True,
        error_messages={"required": "Номер дома обязателен для заполнения."}
    )
    supplier = serializers.PrimaryKeyRelatedField(
        queryset=NetworkNode.objects.all(),
        allow_null=True,
        required=False,
        help_text="ID поставщика (предыдущего звена в сети)"
    )
    supplier_name = serializers.CharField(
        source="supplier.name",
        read_only=True,
        help_text="Название поставщика"
    )
    debt_to_supplier = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        required=False,
        default=0,
        min_value=0,
        help_text="Задолженность в денежном выражении"
    )
    created_at = serializers.DateTimeField(read_only=True)
    level = serializers.IntegerField(read_only=True)

    node_type_display = serializers.CharField(
        source='get_node_type_display',
        read_only=True
    )

    class Meta:
        model = NetworkNode
        fields = [
            "id",  # только для чтения
            "name", # обязателен для заполнения
            "node_type", # обязателен для заполнения
            "node_type_display", # только для чтения
            "email", # обязателен для заполнения
            "phone", # не обязателен для заполнения
            "country", # обязателен для заполнения
            "city", # обязателен для заполнения
            "street", # не обязателен для заполнения
            "house_number", # обязателен для заполнения
            "supplier", # не обязателен для заполнения
            "supplier_name", # только для чтения
            "debt_to_supplier", # не обязателен для заполнения, по умолчанию 0
            "created_at", # только для чтения
            "level", # только для чтения
            "products", # только для чтения
        ]

    def validate(self, data):
        """
        Применяем кастомный валидатор для проверки бизнес - логики.
        """
        validator = NetworkNodeValidator()
        validator(data)
        return data

    def update(self, instance, validated_data):
        # Удаляем debt_to_supplier, если он пришёл в запросе
        validated_data.pop('debt_to_supplier', None)
        return super().update(instance, validated_data)
