import secrets

from django.core import signing
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.views import APIView

from config import settings
from config.settings import DEFAULT_FROM_EMAIL
from users.models import User
from users.serializers import (
    PasswordResetConfirmSerializer,
    PasswordResetSerializer,
    UserSerializer,
)


class UserCreateAPIView(CreateAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = (AllowAny,)

    def perform_create(self, serializer):
        user = serializer.save(is_active=True)
        user.save()


class UserListAPIView(generics.ListAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]


class UserRetrieveAPIView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]


#  поддерживает как put так и putch
class UserUpdateAPIView(generics.UpdateAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]


class UserDestroyAPIView(generics.DestroyAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]


class UserRegisterAPIView(CreateAPIView):
    """
    Представление для регистрации нового пользователя.

    - Принимает email, пароль и другие данные пользователя.
    - Создаёт нового пользователя с полем `is_active=False`.
    - Генерирует токен для подтверждения email.
    - Отправляет письмо со ссылкой для подтверждения email.
    """

    serializer_class = UserSerializer
    permission_classes = (AllowAny,)

    def perform_create(self, serializer):
        user = serializer.save()

        # Генерация токена
        user.token = secrets.token_hex(16)
        user.save()

        # Отправка письма с подтверждением email
        host = self.request.get_host()
        url = f"http://{host}/users/email-confirm/{user.token}/"

        send_mail(
            subject="Подтверждение почты",
            message=f"Привет! Перейдите по ссылке для подтверждения почты: {url}",
            from_email=DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
        )


class PasswordResetAPIView(APIView):
    """
    Представление для запроса сброса пароля.

    Обрабатывает POST-запросы для инициации процесса сброса пароля:
    - Проверяет существование пользователя по email.
    - Генерирует уникальный токен для сброса пароля.
    - Создает закодированный `uid` на основе ID пользователя.
    - Отправляет email со ссылкой для сброса пароля, содержащей `uid` и токен.

    Args:
        request (Request): Объект запроса, содержащий email пользователя.

    Returns:
        Response: JSON-ответ с сообщением об успехе или ошибке.

    Examples:
        Пример запроса:
        ```json
        POST /users/password-reset/
        {
            "email": "user@example.com"
        }
        ```

        Пример успешного ответа:
        ```json
        {
            "message": "Инструкция по сбросу пароля отправлена на ваш email."
        }
        ```

        Пример ошибки:
        ```json
        {
            "error": "Пользователь не активен. Подтвердите email для восстановления пароля."
        }
        ```

    Raises:
        ValidationError: Если пользователь с указанным email не найден или неактивен.

    Notes:
        - `uid` кодируется с использованием `django.core.signing` для безопасности.
        - Ссылка для сброса пароля формируется на основе настроек `PASSWORD_RESET_URL`.
        - Email отправляется с использованием `django.core.mail.send_mail`.
    """

    permission_classes = (AllowAny,)

    def post(self, request):
        # print(f"Данные запроса: {request.data}")  # Отладочный вывод
        serializer = PasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # Генерация токена
        user = serializer.save()
        # Отладочный вывод
        # print(f"Пользователь найден: {user.email}, ID: {user.id}")

        # Проверка, активен ли пользователь
        if not user.is_active:
            return Response(
                {
                    "error": settings.PASSWORD_RESET_SETTINGS[
                        "PASSWORD_RESET_ERROR_MESSAGE"
                    ]
                },
                status=HTTP_400_BAD_REQUEST,
            )

        # Кодируем user.id в uid
        uid = signing.dumps({"user_id": user.id})
        # print(f"Закодированный uid: {uid}")  # Отладочный вывод
        token = user.token

        # Формируем полный URL для сброса пароля
        reset_url_template = settings.PASSWORD_RESET_SETTINGS["PASSWORD_RESET_URL"]
        url = reset_url_template.format(uid=uid, token=token)

        # Определяем протокол (http или https)
        protocol = "https" if request.is_secure() else "http"

        host = request.get_host()
        # url = f"http://{host}/users/password-reset-confirm/{uid}/{user.token}/"
        url = f"{protocol}://{host}/{url}"
        # print(f"Ссылка для сброса пароля: {url}")  # Отладочный вывод

        # send_mail(
        #     subject="Сброс пароля",
        #     message=f"Для сброса пароля перейдите по ссылке: {url}",
        #     from_email=DEFAULT_FROM_EMAIL,
        #     recipient_list=[user.email],
        # )

        send_mail(
            subject=settings.PASSWORD_RESET_SETTINGS["PASSWORD_RESET_EMAIL_SUBJECT"],
            message=settings.PASSWORD_RESET_SETTINGS["PASSWORD_RESET_EMAIL_MESSAGE"]
            + f"{url}",
            from_email=DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
        )

        return Response(
            {
                "message": settings.PASSWORD_RESET_SETTINGS[
                    "PASSWORD_RESET_SUCCESS_MESSAGE"
                ]
            }
        )


class PasswordResetConfirmAPIView(APIView):
    """
    Представление для подтверждения сброса пароля.

    Обрабатывает POST-запросы для завершения процесса сброса пароля:
    - Принимает `uid`, `token` и новый пароль.
    - Проверяет корректность `uid` и `token`.
    - Устанавливает новый пароль пользователю.

    Args:
        request (Request): Объект запроса, содержащий `new_password`.
        uid (str): Закодированный идентификатор пользователя, полученный из ссылки.
        token (str): Токен для сброса пароля, полученный из ссылки.

    Returns:
        Response: JSON-ответ с сообщением об успехе или ошибке.

    Example:
        Пример запроса:
        ```
        POST /users/password-reset-confirm/{uid}/{token}/
        {
            "new_password": "new_secure_password"
        }
        ```

        Пример успешного ответа:
        ```
        {
            "message": "Пароль успешно изменён."
        }
        ```

        Пример ошибки:
        ```
        {
            "error": "Неверный токен."
        }
        ```

    Raises:
        ValidationError: Если данные не прошли валидацию.
            - Если `uid` неверный или не может быть декодирован.
            - Если пользователь с указанным `uid` не найден.
            - Если `token` не совпадает с токеном пользователя.
            - Если пользователь неактивен (не подтвердил email).

    Notes:
        - `uid` декодируется с использованием `django.core.signing`.
        - После успешного сброса пароля токен удаляется.
    """

    permission_classes = (AllowAny,)

    def post(self, request, uid, token):
        # Добавляем uid и token в данные запроса
        request.data.update({"uid": uid, "token": token})
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        serializer.save()  # Сохранение нового пароля

        return Response({"message": "Пароль успешно изменён."})


class EmailVerificationAPIView(APIView):
    """
    Представление для подтверждения email.

    - Принимает токен из ссылки, отправленной на email пользователя.
    - Активирует пользователя (`is_active=True`) при успешной проверке токена.
    - Удаляет токен после успешного подтверждения.
    """

    permission_classes = (AllowAny,)

    def get(self, request, token):
        # Пытаемся найти пользователя с указанным токеном
        user = get_object_or_404(User, token=token)

        if user.is_active:
            return Response(
                {"error": "Email уже подтверждён."}, status=HTTP_400_BAD_REQUEST
            )

        # Активируем пользователя и удаляем токен
        user.is_active = True
        user.token = None
        user.save()

        return Response({"message": "Email успешно подтверждён!"}, status=HTTP_200_OK)
