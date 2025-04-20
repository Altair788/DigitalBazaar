import secrets

from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField

NULLABLE = {"blank": True, "null": True}


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Users must have an email address")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Создает и возвращает суперпользователя с заданным email и паролем."""
        extra_fields.setdefault("is_staff", True)  # Суперпользователь должен быть staff
        extra_fields.setdefault(
            "is_superuser", True
        )  # Суперпользователь должен быть суперпользователем

        # Проверяем, что is_staff и is_superuser установлены в True
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Суперпользователь должен иметь is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Суперпользователь должен иметь is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = None
    email = models.EmailField(
        unique=True, verbose_name="почта", help_text="укажите почту"
    )
    tg_id = models.PositiveIntegerField(
        verbose_name="телеграм - ID", **NULLABLE, help_text="укажите телеграм - ID"
    )
    tg_nick = models.CharField(
        max_length=50,
        verbose_name="телеграм - ник",
        blank=True,
        help_text="укажите ник телеграм",
    )
    first_name = models.CharField(
        max_length=50, blank=True, verbose_name="имя", help_text="укажите имя"
    )
    last_name = models.CharField(
        max_length=50, blank=True, verbose_name="фамилия", help_text="укажите фамилию"
    )
    token = models.CharField(max_length=32, blank=True, null=True)
    is_active = models.BooleanField(default=False)

    phone = PhoneNumberField(
        **NULLABLE,
        unique=True,
        verbose_name="телефон для связи",
        help_text="укажите телефон"
    )
    country = models.CharField(max_length=100, verbose_name="страна", blank=True)

    image = models.ImageField(
        upload_to="users/avatars/",
        verbose_name="аватар",
        help_text="Загрузите аватарку",
        **NULLABLE
    )

    ROLE_USER = "user"
    ROLE_ADMIN = "admin"

    ROLE_CHOICES = [
        (ROLE_USER, "User"),
        (ROLE_ADMIN, "Admin"),
    ]

    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default=ROLE_USER,
        verbose_name="Роль пользователя",
        help_text="Выберите роль пользователя: user или admin",
    )

    def generate_token(self):
        self.token = secrets.token_hex(16)
        self.save()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
