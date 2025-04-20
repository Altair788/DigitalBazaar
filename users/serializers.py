import secrets

from django.core import signing
from rest_framework import serializers

from users.models import User


class UserSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели User.
    """

    id = serializers.IntegerField(read_only=True)
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, style={"input_type": "password"})
    tg_id = serializers.IntegerField(allow_null=True, required=False)
    tg_nick = serializers.CharField(allow_null=True, required=False)
    first_name = serializers.CharField(allow_null=True, required=False)
    last_name = serializers.CharField(allow_null=True, required=False)
    token = serializers.CharField(read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    phone = serializers.CharField(allow_null=True, required=False)
    country = serializers.CharField(allow_null=True, required=False)
    role = serializers.CharField(read_only=True)
    image = serializers.ImageField(
        # Поле может быть пустым
        allow_null=True,
        # Необязательно для заполнения
        required=False,
        # Возвращать полный URL (если настроен MEDIA_URL)
        use_url=True,
    )

    def create(self, validated_data):
        email = validated_data.get("email")

        # Проверка на существование пользователя с таким же email
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError(
                {"email": ["Пользователь с такой почтой уже существует."]}
            )

        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        # Пользователь не активен до подтверждения email
        user.is_active = False
        # Генерация токена для подтверждения email
        user.token = secrets.token_hex(16)
        user.save()
        return user

    class Meta:
        model = User
        fields = (
            "id",  # Только для чтения
            "email",  # Обязателен для заполнения
            "password",  # Только для записи
            "tg_id",  # Не обязателен для заполнения
            "tg_nick",  # Не обязателен для заполнения
            "first_name",  # Не обязателен для заполнения
            "last_name",  # Не обязателен для заполнения
            "token",  # Только для чтения
            "is_active",  # Только для чтения
            "phone",  # Не обязателен для заполнения
            "country",  # Не обязателен для заполнения
            "image",  # Не обязателен для заполнения
            "role",  # Только для чтения
        )


class PasswordResetSerializer(serializers.Serializer):
    """
    Сериализатор для отправки email на сброс пароля
    Этот сериализатор проверяет, существует ли пользователь с указанным email,
    и генерирует токен для сброса пароля
    """

    email = serializers.EmailField()

    def validate_email(self, value):
        # print(f"Проверка email: {value}")  # Отладочный вывод
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Пользователь с таким email не найден.")
        return value

    def save(self):
        user = User.objects.get(email=self.validated_data["email"])
        # print(f"Пользователь найден: {user.email}, ID: {user.id}")  # Отладочный вывод
        # Генерация токена для сброса пароля
        user.token = secrets.token_hex(16)
        user.save()
        return user


class PasswordResetConfirmSerializer(serializers.Serializer):
    """
    Сериализатор для подтверждения сброса пароля.

    Принимает и валидирует данные для сброса пароля:
    - uid: закодированный идентификатор пользователя
    - token: токен для сброса пароля
    - new_password: новый пароль пользователя

    Процесс валидации включает:
    - Декодирование uid и проверку существования пользователя
    - Проверку соответствия токена
    - Проверку активности пользователя

    При успешной валидации устанавливает новый пароль и удаляет токен сброса.

    Attributes:
        uid (str): Закодированный идентификатор пользователя.
        token (str): Токен для сброса пароля.
        new_password (str): Новый пароль пользователя (только для записи).

    Raises:
        ValidationError: Если uid неверный, пользователь не найден, токен неверный,
                         пользователь неактивен или возникли проблемы при сохранении.

    Note:
        Использует django.core.signing для декодирования uid.
    """

    uid = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True)

    def validate(self, data: dict[str, any]):
        uid = data.get("uid")
        token = data.get("token")

        try:
            # Декодируем uid
            decoded_data = signing.loads(uid)
            user_id = decoded_data["user_id"]
        except (signing.BadSignature, KeyError):
            raise serializers.ValidationError(
                {"uid": "Неверный идентификатор пользователя."}
            )

        # Проверяем, существует ли пользователь с таким uid
        user = User.objects.filter(id=user_id).first()
        if not user:
            raise serializers.ValidationError(
                {"uid": "Неверный идентификатор пользователя."}
            )

        # Проверяем, совпадает ли токен
        if user.token != token:
            raise serializers.ValidationError({"token": "Неверный токен."})

        # Проверяем, активен ли пользователь
        if not user.is_active:
            raise serializers.ValidationError(
                {"uid": "Пользователь не активен. Необходимо подтвердить email"}
            )

        return data

    def save(self) -> None:
        # Декодируем uid
        decoded_data = signing.loads(self.validated_data["uid"])
        user_id = decoded_data["user_id"]

        user = User.objects.get(id=user_id, token=self.validated_data["token"])
        user.set_password(self.validated_data["new_password"])
        # Удаляем токен после успешного сброса пароля
        user.token = None
        user.save()
