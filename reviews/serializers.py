from rest_framework import serializers

from ads.models import Ad
from reviews.models import Review
from reviews.validators import ReviewValidator


class ReviewSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Review.
    """

    id = serializers.IntegerField(read_only=True)
    text = serializers.CharField(required=True)
    author = serializers.PrimaryKeyRelatedField(read_only=True)
    ad = serializers.PrimaryKeyRelatedField(queryset=Ad.objects.all())
    created_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Review
        fields = (
            "id",
            "text",
            "author",
            "ad",
            "created_at",
        )

    def validate(self, data):
        """
        Применяем кастомный валидатор для проверки бизнес-логики.
        """
        validator = ReviewValidator()
        validator(data)
        return data
