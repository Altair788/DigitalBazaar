import os
from typing import Union

from django.core.files.uploadedfile import UploadedFile
from rest_framework.exceptions import ValidationError


class AdValidator:
    """
    Валидатор для проверки бизнес-логики объявлений.
    """

    def __call__(self, data: dict[str, any]) -> None:
        # для реализации PATCH - запроса
        if "title" in data:
            title = data.get("title")
            self.validate_title(title)
        if "price" in data:
            price = data.get("price")
            self.validate_price(price)
        if "description" in data:
            description = data.get("description")
            self.validate_description(description)
        if "image" in data:
            image = data.get("image")
            self.validate_image(image)

    def validate_title(self, title: str) -> None:
        """
        Проверка названия объявления
        Args:
            title(str): Название объявления

        Raises:
            ValidationError: Название товара обязательно для заполнения.
                             Название должно содержать минимум 2 символа.
        Returns:
            None
        """
        if not title:
            raise ValidationError("Название товара обязательно для заполнения.")

        if len(title) < 2:
            raise ValidationError("Название должно содержать минимум 2 символа.")

    def validate_price(self, price: int) -> None:
        """
        Проверка стоимости товара в объявлении
        Args:
            price(int): Стоимость товара в объявлении

        Raises:
            ValidationError: Поле цены обязательно для заполнения.
                             Цена должна быть положительным числом.
        Returns:
            None
        """
        # if not price:
        #     raise ValidationError("Поле цены обязательно для заполнения.")

        if price is None:
            raise ValidationError("Поле цены обязательно для заполнения.")

        if price <= 0:
            raise ValidationError("Цена должна быть положительным числом.")

    def validate_description(self, description: str) -> None:
        """
        Проверка описания товара в объявлении
        Args:
            description(str): Описание товара в объявлении

        Raises:
            ValidationError: Описание не может превышать 1000 символов.
        Returns:
            None
        """
        if description:
            if len(description) > 1000:
                raise ValidationError("Описание не может превышать 1000 символов.")

    def validate_image(self, image: Union[UploadedFile, None]):
        """
        Проверка изображения.
        Args:
            image (Union[UploadedFile, None]): Изображение товара или None

        Raises:
            ValidationError: Неподдерживаемый формат изображения.
                             Допустимые форматы: JPG, JPEG, PNG, WEBP.
                             Размер изображения не должен превышать 5MB.
        Returns:
            None
        """

        if image:
            # Проверка расширения файла
            ext = os.path.splitext(image.name)[1].lower()
            valid_extensions = [".jpg", ".jpeg", ".png", ".webp"]
            if ext not in valid_extensions:
                raise ValidationError(
                    "Неподдерживаемый формат изображения. "
                    "Допустимые форматы: JPG, JPEG, PNG, WEBP."
                )

            # Проверка размера файла (не более 5 MB)
            max_size = 5 * 1024 * 1024
            if image.size > max_size:
                raise ValidationError("Размер изображения не должен превышать 5MB.")
