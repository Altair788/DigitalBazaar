from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from ads.models import Ad
from users.models import User


class Review(models.Model):
    """
    Модель, представляющая отзыв.

    Атрибуты:
        text (str): Текст отзыва.
        author (ForeignKey): Пользователь, оставивший отзыв.
        ad (ForeignKey): Объявление, под которым оставлен отзыв.
        created_at (DateTimeField): Дата и время создания отзыва.
    """

    text = models.TextField(
        verbose_name="Текст отзыва",
        help_text="Укажите текст отзыва",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Автор отзыва",
        help_text="Пользователь, оставивший этот отзыв",
        related_name="reviews",
    )
    ad = models.ForeignKey(
        Ad,
        on_delete=models.CASCADE,
        verbose_name="Объявление",
        help_text="Объявление, под которым оставлен отзыв",
        related_name="reviews",
    )
    created_at = models.DateTimeField(
        default=timezone.now,
        verbose_name="Дата и время создания",
        help_text="Укажите дату и время создания отзыва",
    )

    def clean(self):
        """
        Проверка бизнес-логики на уровне модели для валидации в админ - панели.
        """
        # Проверка: текст отзыва не может быть пустым.
        if not self.text:
            raise ValidationError("Текст отзыва обязателен.")

        # Проверка: отзыв не может быть оставлен на собственное объявление.
        if self.author == self.ad.author:
            raise ValidationError("Нельзя оставлять отзыв на своё объявление.")

    def __repr__(self) -> str:
        """Возвращает строковое представление объекта Отзыв.

        Returns:
            str: Строковое представление объекта с его атрибутами.
                  Например: Review(text=..., author=..., ...)
        """
        return f"""Review(
text={self.text},
author={self.author},
ad={self.ad},
created_at={self.created_at})"""

    def __str__(self) -> str:
        """Возвращает строковое представление отзыва.

        Returns:
            str: Краткое описание отзыва.
                  Например: "Отзыв от пользователя на объявление 'Ноутбук'".
        """
        return f"Отзыв от {self.author} на объявление '{self.ad.title}'"

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
        ordering = ["-created_at"]
