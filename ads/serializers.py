from rest_framework import serializers

from ads.models import Ad
from ads.validators import AdValidator


class AdSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Ad.
    """

    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField(
        required=True, error_messages={"required": "Название товара обязательно."}
    )
    price = serializers.IntegerField(
        required=True, error_messages={"required": "Указание цены обязательно."}
    )
    description = serializers.CharField(allow_null=True, required=False)
    author = serializers.PrimaryKeyRelatedField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    image = serializers.ImageField(
        # Поле может быть пустым
        allow_null=True,
        # Необязательно для заполнения
        required=False,
        # Возвращает полный URL (если настроен MEDIA_URL)
        use_url=True,
    )

    class Meta:
        model = Ad
        fields = (
            "id",  # Только для чтения
            "title",  # Обязателен для заполнения
            "price",  # Обязателен для заполнения
            "description",  # Не обязателен для заполнения
            "author",  # Только для чтения
            "created_at",  # Только для чтения
            "image",  # Не обязателен для заполнения
        )

    def validate(self, data):
        """
        Применяем кастомный валидатор для проверки бизнес - логики.
        """
        validator = AdValidator()
        validator(data)
        return data
