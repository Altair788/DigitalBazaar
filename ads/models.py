from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from users.models import User

NULLABLE = {"null": True, "blank": True}


class Ad(models.Model):
    """
    Модель, представляющая объявление.

    Атрибуты:
        title (str): Название товара.
        price (int): Цена товара.
        description (str): Описание товара.
        author (ForeignKey): Пользователь, создавший объявление.
        created_at (DateTimeField): Дата и время создания объявления.
        image (ImageField): Изображение товара (опционально).
    """

    title = models.CharField(
        max_length=200,
        verbose_name="Название товара",
        help_text="Укажите название товара",
    )
    price = models.PositiveIntegerField(
        verbose_name="Цена товара",
        help_text="Укажите цену товара",
    )
    description = models.TextField(
        verbose_name="Описание товара",
        help_text="Укажите описание товара",
        blank=True,
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Автор объявления",
        help_text="Пользователь, создавший это объявление",
        related_name="ads",
    )
    created_at = models.DateTimeField(
        default=timezone.now,
        verbose_name="Дата и время создания",
        help_text="Укажите дату и время создания объявления",
    )
    image = models.ImageField(
        upload_to="ads/images/",
        verbose_name="Изображение товара",
        help_text="Загрузите изображение товара",
        **NULLABLE,
    )

    def clean(self):
        """
        Проверка бизнес-логики на уровне модели (для валидации в админ - панели)
        """
        # Проверка: цена не может быть отрицательной.
        if self.price < 0:
            raise ValidationError("Цена товара не может быть отрицательной.")

        if not self.price:
            raise ValidationError("Указание цены обязательно.")

        # Проверка: название не может быть пустым.
        if not self.title:
            raise ValidationError("Название товара обязательно.")

    def __repr__(self) -> str:
        """Возвращает строковое представление объекта Объявление.

        Returns:
            str: Строковое представление объекта с его атрибутами.
                  Например: Ad(title=..., price=..., ...)
        """
        return f"""Ad(
title={self.title},
price={self.price},
description={self.description},
author={self.author},
created_at={self.created_at},
image={self.image})"""

    def __str__(self) -> str:
        """Возвращает строковое представление объявления.

        Returns:
            str: Название товара.
                  Например: "Ноутбук".
        """
        return self.title

    class Meta:
        verbose_name = "Объявление"
        verbose_name_plural = "Объявления"
        # Сортировка по дате создания (новые выше)
        ordering = ["-created_at"]
