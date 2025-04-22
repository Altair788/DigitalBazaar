import json

from django.contrib.auth.models import Group
from django.core import mail, signing
from django.core.mail import EmailMessage
from django.core.management import call_command
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIRequestFactory, APITestCase

from users.models import User
from users.permissions import IsAdmin
from users.serializers import PasswordResetConfirmSerializer


#  тестирование методов модели User
class UserModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com", password="password123", is_active=True
        )

    def test_create_user(self):
        """
        Проверяет создание обычного пользователя.
        """
        self.assertEqual(self.user.email, "test@example.com")
        self.assertTrue(self.user.check_password("password123"))
        self.assertTrue(self.user.is_active)

    def test_create_user_without_email(self):
        """
        Проверяет, что создание пользователя без email вызывает исключение.
        """
        with self.assertRaises(ValueError) as context:
            User.objects.create_user(email=None, password="password123")
        self.assertEqual(str(context.exception), "Users must have an email address")

    def test_create_superuser(self):
        """
        Проверяет создание суперпользователя.
        """
        superuser = User.objects.create_superuser(
            email="admin@example.com", password="adminpassword"
        )
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)

    def test_create_superuser_without_is_staff(self):
        """
        Проверяет, что создание суперпользователя с is_staff=False вызывает исключение.
        """
        with self.assertRaises(ValueError) as context:
            User.objects.create_superuser(
                email="admin@example.com",
                password="adminpassword",
                is_staff=False,
            )
        self.assertEqual(
            str(context.exception), "Суперпользователь должен иметь is_staff=True."
        )

    def test_create_superuser_without_is_superuser(self):
        """
        Проверяет, что создание суперпользователя с is_superuser=False вызывает исключение.
        """
        with self.assertRaises(ValueError) as context:
            User.objects.create_superuser(
                email="admin@example.com",
                password="adminpassword",
                is_superuser=False,
            )
        self.assertEqual(
            str(context.exception), "Суперпользователь должен иметь is_superuser=True."
        )

    def test_generate_token(self):
        """
        Проверяет генерацию токена для пользователя.
        """
        self.user.generate_token()
        self.assertIsNotNone(self.user.token)


#  Тесты для регистрации пользователя


class UserRegisterAPIViewTest(APITestCase):
    def test_register_user(self):
        """
        Проверяет регистрацию нового пользователя.
        """
        data = {
            "email": "newuser@example.com",
            "password": "newpassword123",
            "phone": "+1234567890",
            "country": "USA",
        }

        response = self.client.post(
            "/users/register/", data=json.dumps(data), content_type="application/json"
        )

        # Проверяем статус ответа
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Проверяем, что пользователь создан
        user = User.objects.get(email="newuser@example.com")
        self.assertFalse(
            user.is_active
        )  # Пользователь должен быть неактивным по умолчанию


#  Тесты для подтверждения email
class EmailVerificationAPIViewTest(APITestCase):
    """
    Проверяет подтверждение email пользователя.
    """

    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com", password="password123", token="testtoken"
        )

    def test_email_verification(self):
        """
        Тест подтверждения email.
        """
        response = self.client.get(f"/users/email-confirm/{self.user.token}/")

        # Проверяем статус ответа
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Проверяем, что пользователь активирован и токен удалён
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)
        self.assertIsNone(self.user.token)


#  Тесты для сброса пароля
class PasswordResetAPIViewTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com", password="password123", is_active=True
        )

        # print(f"Пользователь в базе данных: {User.objects.all()}")  # Отладочный вывод

    def test_password_reset_request(self):
        """
        Проверяет запрос на сброс пароля:
        - Генерация токена.
        - Отправка email с инструкцией.
        """
        data = {"email": "test@example.com"}

        response = self.client.post(
            "/users/password-reset/",
            data=json.dumps(data),
            content_type="application/json",
        )
        # Проверяем статус ответа
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Проверяем, что токен сгенерирован
        self.user.refresh_from_db()
        self.assertIsNotNone(self.user.token)

        # Проверяем, что сообщение содержит текст
        message = response.data.get("message", "")
        self.assertEqual(
            message, "Инструкция по сбросу пароля отправлена на ваш email."
        )

        # Проверяем, что письмо было отправлено
        outbox: list[EmailMessage] = mail.outbox
        # Должно быть одно письмо в outbox
        self.assertEqual(len(outbox), 1)

        # Проверяем содержимое письма
        email = outbox[0]
        self.assertEqual(email.subject, "Сброс пароля")
        self.assertEqual(email.to, ["test@example.com"])
        # Проверяем, что тело письма содержит ссылку
        self.assertIn("http://", email.body)


class PasswordResetConfirmAPIViewTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com",
            password="password123",
            token="testtoken",
            is_active=True,
        )

        # Кодируем uid для использования в тестах
        self.uid = signing.dumps({"user_id": self.user.id})

    def test_password_reset_confirm(self):
        """
        Проверяет успешное подтверждение сброса пароля.
        """
        data = {
            "uid": self.uid,
            "token": "testtoken",
            "new_password": "newpassword123",
        }
        url = f"/users/password-reset-confirm/{self.uid}/{self.user.token}/"

        response = self.client.post(
            url,
            data=json.dumps(data),
            content_type="application/json",
        )

        # Проверяем статус ответа
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Проверяем, что пароль обновлён и токен удалён
        self.user.refresh_from_db()

        self.assertTrue(self.user.check_password("newpassword123"))
        self.assertIsNone(self.user.token)

    def test_password_reset_confirm_inactive_user(self):
        """
        Проверяет сброс пароля для неактивного пользователя.
        """
        self.user.is_active = False
        self.user.save()

        data = {
            "uid": self.uid,
            "token": "testtoken",
            "new_password": "newpassword123",
        }

        url = f"/users/password-reset-confirm/{self.uid}/{self.user.token}/"

        response = self.client.post(
            url,
            data=json.dumps(data),
            content_type="application/json",
        )

        # Проверяем статус ответа
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data.get("uid")[0],
            "Пользователь не активен. Необходимо подтвердить email",
        )


class CreateUsersCommandTest(TestCase):
    def setUp(self):
        # Устанавливаем переменные окружения для тестов
        self.superuser_email = "admin@example.com"
        self.superuser_password = "adminpassword"
        self.normal_user_email = "user@example.com"
        self.normal_user_password = "userpassword"

        # Мокаем переменные окружения
        import os

        os.environ["SUPERUSER_EMAIL"] = self.superuser_email
        os.environ["SUPERUSER_PASSWORD"] = self.superuser_password
        os.environ["NORMAL_USER_EMAIL"] = self.normal_user_email
        os.environ["NORMAL_USER_PASSWORD"] = self.normal_user_password

    def test_create_users_command(self):
        """
        Проверяет, что команда create_users корректно создает суперпользователя и обычного пользователя.
        """
        # Вызываем команду create_users
        call_command("csu")

        # Проверяем, что суперпользователь создан
        superuser = User.objects.filter(email=self.superuser_email).first()
        self.assertIsNotNone(superuser)
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)
        self.assertEqual(superuser.role, User.ROLE_ADMIN)
        self.assertTrue(superuser.check_password(self.superuser_password))

        # Проверяем, что обычный пользователь создан
        normal_user = User.objects.filter(email=self.normal_user_email).first()
        self.assertIsNotNone(normal_user)
        self.assertFalse(normal_user.is_staff)
        self.assertFalse(normal_user.is_superuser)
        self.assertEqual(normal_user.role, User.ROLE_USER)
        self.assertTrue(normal_user.check_password(self.normal_user_password))

    def test_create_users_command_with_existing_users(self):
        """
        Проверяет, что команда create_users не создает дубликаты пользователей, если они уже существуют.
        """
        # Создаем суперпользователя и обычного пользователя вручную
        User.objects.create_superuser(
            email=self.superuser_email,
            password=self.superuser_password,
            role=User.ROLE_ADMIN,
        )
        User.objects.create_user(
            email=self.normal_user_email,
            password=self.normal_user_password,
        )

        # Вызываем команду create_users
        call_command("csu")

        # Проверяем, что количество пользователей не изменилось
        self.assertEqual(User.objects.count(), 2)

        # Проверяем, что суперпользователь и обычный пользователь остались без изменений
        superuser = User.objects.get(email=self.superuser_email)
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)
        self.assertEqual(superuser.role, User.ROLE_ADMIN)

        normal_user = User.objects.get(email=self.normal_user_email)
        self.assertFalse(normal_user.is_staff)
        self.assertFalse(normal_user.is_superuser)
        self.assertEqual(normal_user.role, User.ROLE_USER)


#
# class CanViewAPITest(APITestCase):
#     def setUp(self):
#         self.factory = APIRequestFactory()
#         self.user = User.objects.create_user(
#             email="user@example.com", password="password123", is_staff=False
#         )
#         self.staff_user = User.objects.create_user(
#             email="staff@example.com", password="password123", is_staff=True
#         )
#         self.permission = CanViewAPI()  # Используем ваш класс
#
#     def test_has_permission_for_staff_user(self):
#         """
#         Проверяет, что пользователь с is_staff=True имеет доступ.
#         """
#         request = self.factory.get("/some-endpoint/")
#         request.user = self.staff_user
#         self.assertTrue(self.permission.has_permission(request, None))
#
#     def test_has_permission_for_non_staff_user(self):
#         """
#         Проверяет, что пользователь с is_staff=False не имеет доступа.
#         """
#         request = self.factory.get("/some-endpoint/")
#         request.user = self.user
#         self.assertFalse(self.permission.has_permission(request, None))


class IsAdminTest(APITestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create_user(
            email="user@example.com", password="password123"
        )
        self.admin_user = User.objects.create_user(
            email="admin@example.com", password="password123"
        )
        self.admin_group = Group.objects.create(name="admins")
        self.admin_user.groups.add(self.admin_group)
        self.permission = IsAdmin()  # Используем ваш класс

    def test_has_permission_for_admin_user(self):
        """
        Проверяет, что пользователь в группе admins имеет доступ.
        """
        request = self.factory.get("/some-endpoint/")
        request.user = self.admin_user
        self.assertTrue(self.permission.has_permission(request, None))

    def test_has_permission_for_non_admin_user(self):
        """
        Проверяет, что пользователь не в группе admins не имеет доступа.
        """
        request = self.factory.get("/some-endpoint/")
        request.user = self.user
        self.assertFalse(self.permission.has_permission(request, None))



class PasswordResetConfirmSerializerTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com", password="password123", is_active=True
        )
        self.user.token = "valid_token"
        self.user.save()

    def test_valid_data(self):
        """
        Проверяет успешную валидацию при корректных данных.
        """
        uid = signing.dumps({"user_id": self.user.id})
        data = {
            "uid": uid,
            "token": "valid_token",
            "new_password": "newpassword123",
        }
        serializer = PasswordResetConfirmSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_invalid_uid(self):
        """
        Проверяет ошибку при неверном uid.
        """
        data = {
            "uid": "invalid_uid",
            "token": "valid_token",
            "new_password": "newpassword123",
        }
        serializer = PasswordResetConfirmSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(
            serializer.errors["uid"][0], "Неверный идентификатор пользователя."
        )

    def test_user_not_found(self):
        """
        Проверяет ошибку, если пользователь с указанным uid не существует.
        """
        uid = signing.dumps({"user_id": 9999})  # Несуществующий user_id
        data = {
            "uid": uid,
            "token": "valid_token",
            "new_password": "newpassword123",
        }
        serializer = PasswordResetConfirmSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(
            serializer.errors["uid"][0], "Неверный идентификатор пользователя."
        )

    def test_invalid_token(self):
        """
        Проверяет ошибку при неверном токене.
        """
        uid = signing.dumps({"user_id": self.user.id})
        data = {
            "uid": uid,
            "token": "invalid_token",
            "new_password": "newpassword123",
        }
        serializer = PasswordResetConfirmSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(serializer.errors["token"][0], "Неверный токен.")

    def test_inactive_user(self):
        """
        Проверяет ошибку, если пользователь неактивен.
        """
        self.user.is_active = False
        self.user.save()
        uid = signing.dumps({"user_id": self.user.id})
        data = {
            "uid": uid,
            "token": "valid_token",
            "new_password": "newpassword123",
        }
        serializer = PasswordResetConfirmSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(
            serializer.errors["uid"][0],
            "Пользователь не активен. Необходимо подтвердить email",
        )

    def test_bad_signature(self):
        """
        Проверяет ошибку при неверной подписи uid.
        """
        uid = "invalid_uid_with_bad_signature"
        data = {
            "uid": uid,
            "token": "valid_token",
            "new_password": "newpassword123",
        }
        serializer = PasswordResetConfirmSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(
            serializer.errors["uid"][0], "Неверный идентификатор пользователя."
        )

    def test_missing_user_id(self):
        """
        Проверяет ошибку, если в декодированном uid отсутствует user_id.
        """
        uid = signing.dumps({"some_key": "some_value"})  # Нет user_id
        data = {
            "uid": uid,
            "token": "valid_token",
            "new_password": "newpassword123",
        }
        serializer = PasswordResetConfirmSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(
            serializer.errors["uid"][0], "Неверный идентификатор пользователя."
        )
