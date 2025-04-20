import json

from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.test import APITestCase

from ads.models import Ad
from ads.validators import AdValidator
from reviews.models import Review
from users.models import User


# Create your tests here.
class AdTestCase(APITestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(
            email="test@example.com", password="testpass", is_active=True
        )
        # Аутентифицируем клиент
        self.client.force_authenticate(user=self.user)

    def test_create_ad(self):
        """
        Тестирование создания объявления
        """
        data = {"title": "book", "price": 1200}

        url = reverse("ads:ads-create")

        response = self.client.post(
            url, data=json.dumps(data), content_type="application/json"
        )

        # 1 гипотеза
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # 2 гипотеза
        response_data = response.json()
        self.assertEqual(response_data["id"], 1)
        self.assertEqual(response_data["title"], "book")
        self.assertEqual(response_data["price"], 1200)
        self.assertEqual(response_data["description"], "")
        self.assertEqual(response_data["author"], self.user.id)
        self.assertIsNone(response_data["image"])
        self.assertIn("createdAt", response_data)

        # 3 гипотеза - тест на то, что объект сохранен в БД
        ad = Ad.objects.get(title="book")
        self.assertEqual(ad.price, 1200)
        self.assertEqual(ad.author, self.user)

    def test_list_ad(self):
        """
        Тестирование вывода списка объявлений.
        """

        Ad.objects.create(title="yacht", price=650000, author=self.user)

        Ad.objects.create(title="car", price=250000, author=self.user)

        url = reverse("ads:ads-list")
        response = self.client.get(url)

        # 1 гипотеза
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 2 гипотеза (структура ответа)
        response_data = response.json()

        # Проверяем количество объявлений в списке
        self.assertEqual(response_data["count"], 2)
        self.assertEqual(len(response_data["results"]), 2)

        # Проверяем содержимое первого объявления (чем новее тем выше, согласно ТЗ)
        self.assertEqual(response_data["results"][0]["title"], "car")
        self.assertEqual(response_data["results"][0]["price"], 250000)
        self.assertEqual(response_data["results"][0]["author"], self.user.id)

        # Проверяем содержимое второго объявления
        self.assertEqual(response_data["results"][1]["title"], "yacht")
        self.assertEqual(response_data["results"][1]["price"], 650000)
        self.assertEqual(response_data["results"][1]["author"], self.user.id)

    def test_retrieve_ad(self):
        """
        Тестирование просмотра 1 объявления
        """
        ad1 = Ad.objects.create(title="moto", price=120000, author=self.user)

        url = reverse("ads:ads-retrieve", kwargs={"pk": ad1.pk})

        response = self.client.get(url)

        # 1 гипотеза
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 2 гипотеза (структура ответа)
        response_data = response.json()
        self.assertEqual(response_data["id"], ad1.id)
        self.assertEqual(response_data["title"], "moto")
        self.assertEqual(response_data["price"], 120000)
        self.assertEqual(response_data["author"], self.user.id)

    def test_retrieve_nonexistent_ad(self):
        """
        Тестирование попытки просмотра несуществующего объявления
        """
        url = reverse("ads:ads-retrieve", kwargs={"pk": 9999})
        response = self.client.get(url)

        # 1 гипотеза
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_patch_ad(self):
        ad1 = Ad.objects.create(title="moto", price=120000, author=self.user)

        url = reverse("ads:ads-update", kwargs={"pk": ad1.pk})

        data = {"title": "car"}

        response = self.client.patch(
            url, data=json.dumps(data), content_type="application/json"
        )

        # 1 гипотеза
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 2 гипотеза - проверка, что данные действительно обновились
        ad1.refresh_from_db()
        self.assertEqual(ad1.title, "car")

        # 3 гипотеза - проверка содержимого ответа (цена должна остаться прежней)
        response_data = response.json()
        self.assertEqual(response_data["title"], "car")
        self.assertEqual(response_data["price"], 120000)

    def test_put_ad(self):
        ad1 = Ad.objects.create(
            title="moto", price=120000, author=self.user, description="Old description"
        )

        url = reverse("ads:ads-update", kwargs={"pk": ad1.pk})

        data = {"title": "car", "price": 90000, "description": "New description"}

        response = self.client.put(
            url, data=json.dumps(data), content_type="application/json"
        )

        # 1 гипотеза
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 2 гипотеза - проверка, что данные действительно обновились
        ad1.refresh_from_db()
        self.assertEqual(ad1.title, "car")
        self.assertEqual(ad1.price, 90000)
        self.assertEqual(ad1.description, "New description")

        # 3 гипотеза - проверка содержимого ответа (цена должна остаться прежней)
        response_data = response.json()
        self.assertEqual(response_data["title"], "car")
        self.assertEqual(response_data["price"], 90000)
        self.assertEqual(response_data["description"], "New description")

        # 4 гипотеза - проверка, что автор не изменился
        self.assertEqual(ad1.author, self.user)
        self.assertEqual(response_data["author"], self.user.id)

    def test_delete_ad(self):
        """
        Тестирование удаления объявления.
        """
        # Создаем объявление
        ad = Ad.objects.create(title="moto", price=120000, author=self.user)

        # Убедимся, что объявление существует в базе данных
        self.assertTrue(Ad.objects.filter(id=ad.id).exists())

        # URL для удаления объявления
        url = reverse("ads:ads-delete", kwargs={"pk": ad.pk})

        # Отправляем DELETE-запрос
        response = self.client.delete(url)

        # Проверяем статус ответа
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Проверяем, что объявление больше не существует в базе данных
        self.assertFalse(Ad.objects.filter(id=ad.id).exists())

    def test_filter_ads_by_title(self):
        """
        Проверяет фильтрацию объявлений по названию.
        """
        # Создаем несколько объявлений
        Ad.objects.create(
            title="Ноутбук Apple MacBook Pro", price=150000, author=self.user
        )
        Ad.objects.create(
            title="Смартфон Samsung Galaxy S21", price=80000, author=self.user
        )
        Ad.objects.create(
            title="Наушники Sony WH-1000XM4", price=25000, author=self.user
        )

        # Проверяем, что объявления созданы
        # ads = Ad.objects.all()
        # print("Объявления в базе:", ads)

        # Фильтруем объявления по ключевому слову "ноутбук"
        url = reverse("ads:ads-list")
        # регистронезависимый поиск
        response = self.client.get(url, {"title": "ноутбук"})

        # # Выводим ответ для отладки
        # print("Ответ фильтрации:", response.json())

        # 1 гипотеза
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 2 гипотеза (структура ответа)
        response_data = response.json()
        # print(response_data)

        # Проверяем количество найденных объявлений
        self.assertEqual(response_data["count"], 1)
        self.assertEqual(len(response_data["results"]), 1)

        # Проверяем содержимое найденного объявления
        self.assertEqual(
            response_data["results"][0]["title"], "Ноутбук Apple MacBook Pro"
        )
        self.assertEqual(response_data["results"][0]["price"], 150000)
        self.assertEqual(response_data["results"][0]["author"], self.user.id)

        # Фильтруем объявления по ключевому слову "Samsung"
        response = self.client.get(url, {"title": "Samsung"})

        # 3 гипотеза
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 4 гипотеза (структура ответа)
        response_data = response.json()

        # Проверяем количество найденных объявлений
        self.assertEqual(response_data["count"], 1)
        self.assertEqual(len(response_data["results"]), 1)

        # Проверяем содержимое найденного объявления
        self.assertEqual(
            response_data["results"][0]["title"], "Смартфон Samsung Galaxy S21"
        )
        self.assertEqual(response_data["results"][0]["price"], 80000)
        self.assertEqual(response_data["results"][0]["author"], self.user.id)

        # Фильтруем объявления по ключевому слову, которого нет в названиях
        response = self.client.get(url, {"title": "несуществующий"})

        # 5 гипотеза
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 6 гипотеза (структура ответа)
        response_data = response.json()

        # Проверяем, что объявления не найдены
        self.assertEqual(response_data["count"], 0)
        self.assertEqual(len(response_data["results"]), 0)

    def test_create_ad_without_price(self):
        """
        Проверяет, что нельзя создать объявление без указания цены.
        """
        data = {"title": "No Price Ad"}

        url = reverse("ads:ads-create")

        response = self.client.post(
            url, data=json.dumps(data), content_type="application/json"
        )

        # Ожидаем ошибку валидации
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        #  Проверяем, что ошибка связана с полем "price"
        response_data = response.json()
        self.assertIn("price", response_data)
        # Проверяем текст ошибки
        self.assertEqual(response_data["price"], ["Указание цены обязательно."])

    def test_create_ad_without_title(self):
        """
        Проверяет, что нельзя создать объявление без указания названия.
        """
        data = {"price": 1000}

        url = reverse("ads:ads-create")

        response = self.client.post(
            url, data=json.dumps(data), content_type="application/json"
        )

        # Ожидаем ошибку валидации
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Проверяем, что ошибка связана с полем "title"
        response_data = response.json()
        self.assertIn("title", response_data)
        self.assertEqual(response_data["title"], ["Название товара обязательно."])

    def test_ad_repr(self):
        """
        Проверяет строковое представление объекта Ad (__repr__).
        """
        ad = Ad.objects.create(
            title="Ноутбук Apple MacBook Pro",
            price=150000,
            description="Мощный ноутбук для работы",
            author=self.user,
        )

        expected_repr = f"""Ad(
title={ad.title},
price={ad.price},
description={ad.description},
author={ad.author},
created_at={ad.created_at},
image={ad.image})"""

        self.assertEqual(repr(ad), expected_repr)

    def test_ad_str(self):
        """
        Проверяет строковое представление объекта Ad (__str__).
        """
        ad = Ad.objects.create(
            title="Ноутбук Apple MacBook Pro",
            price=150000,
            description="Мощный ноутбук для работы",
            author=self.user,
        )

        self.assertEqual(str(ad), "Ноутбук Apple MacBook Pro")


class FillDbCommandTest(TestCase):
    def test_fill_db_command(self):
        """
        Проверяет, что команда fill_db корректно создает тестовые данные.
        """
        # Вызываем команду fill_db
        call_command("fill_db")

        # Проверяем, что пользователи созданы
        users = User.objects.all()
        self.assertEqual(users.count(), 2)

        # Проверяем, что объявления созданы
        ads = Ad.objects.all()
        self.assertEqual(ads.count(), 3)

        # Проверяем, что отзывы созданы
        reviews = Review.objects.all()
        self.assertEqual(reviews.count(), 4)

        # Проверяем данные первого пользователя
        user1 = User.objects.get(email="user1@example.com")
        self.assertEqual(user1.first_name, "Иван")
        self.assertEqual(user1.last_name, "Петров")
        self.assertEqual(user1.phone, "+79161234567")
        self.assertEqual(user1.role, User.ROLE_ADMIN)

        # Проверяем данные второго пользователя
        user2 = User.objects.get(email="user2@example.com")
        self.assertEqual(user2.first_name, "Мария")
        self.assertEqual(user2.last_name, "Сидорова")
        self.assertEqual(user2.phone, "+79167654321")
        self.assertEqual(user2.role, User.ROLE_USER)

        # Проверяем данные объявлений
        ad1 = Ad.objects.get(title="Продам ноутбук Apple MacBook Pro")
        self.assertEqual(ad1.price, 150000)
        self.assertEqual(ad1.description, "Отличное состояние, 2023 года выпуска")
        self.assertEqual(ad1.author, user1)

        ad2 = Ad.objects.get(title="Сдам 2-комнатную квартиру")
        self.assertEqual(ad2.price, 35000)
        self.assertEqual(ad2.description, "Центр города, свежий ремонт")
        self.assertEqual(ad2.author, user2)

        ad3 = Ad.objects.get(title="Продам велосипед горный")
        self.assertEqual(ad3.price, 25000)
        self.assertEqual(ad3.description, "Пробег 200 км, идеальное состояние")
        self.assertEqual(ad3.author, user1)

        # Проверяем данные отзывов
        review1 = Review.objects.get(text="Отличный ноутбук, всё работает идеально!")
        self.assertEqual(review1.author, user2)
        self.assertEqual(review1.ad, ad1)

        review2 = Review.objects.get(text="Дороговато, но качество того стоит")
        self.assertEqual(review2.author, user1)
        self.assertEqual(review2.ad, ad1)

        review3 = Review.objects.get(text="Квартира соответствует описанию")
        self.assertEqual(review3.author, user1)
        self.assertEqual(review3.ad, ad2)

        review4 = Review.objects.get(text="Велосипед как новый, рекомендую!")
        self.assertEqual(review4.author, user2)
        self.assertEqual(review4.ad, ad3)


class AdValidatorTest(TestCase):
    def setUp(self):
        self.validator = AdValidator()

    def test_validate_title_empty(self):
        """
        Проверяет, что пустое название вызывает ValidationError.
        """
        with self.assertRaises(ValidationError) as context:
            self.validator.validate_title("")
        self.assertEqual(
            str(context.exception.detail[0]),
            "Название товара обязательно для заполнения.",
        )

    def test_validate_title_too_short(self):
        """
        Проверяет, что название менее 2 символов вызывает ValidationError.
        """
        with self.assertRaises(ValidationError) as context:
            self.validator.validate_title("a")
        self.assertEqual(
            str(context.exception.detail[0]),
            "Название должно содержать минимум 2 символа.",
        )

    def test_validate_title_valid(self):
        """
        Проверяет, что корректное название не вызывает ошибок.
        """
        try:
            self.validator.validate_title("Valid title")
        except ValidationError:
            self.fail("validate_title вызвал ValidationError для корректного названия.")

    def test_validate_price_empty(self):
        """
        Проверяет, что пустая цена вызывает ValidationError.
        """
        with self.assertRaises(ValidationError) as context:
            self.validator.validate_price(None)
        self.assertEqual(
            str(context.exception.detail[0]), "Поле цены обязательно для заполнения."
        )

    def test_validate_price_negative(self):
        """
        Проверяет, что отрицательная цена вызывает ValidationError.
        """
        with self.assertRaises(ValidationError) as context:
            self.validator.validate_price(-100)
        self.assertEqual(
            str(context.exception.detail[0]), "Цена должна быть положительным числом."
        )

    def test_validate_price_zero(self):
        """
        Проверяет, что цена равная нулю вызывает ValidationError.
        """
        with self.assertRaises(ValidationError) as context:
            self.validator.validate_price(0)
        self.assertEqual(
            str(context.exception.detail[0]), "Цена должна быть положительным числом."
        )

    def test_validate_price_valid(self):
        """
        Проверяет, что корректная цена не вызывает ошибок.
        """
        try:
            self.validator.validate_price(1000)
        except ValidationError:
            self.fail("validate_price вызвал ValidationError для корректной цены.")

    def test_validate_description_too_long(self):
        """
        Проверяет, что описание длиннее 1000 символов вызывает ValidationError.
        """
        long_description = "a" * 1001
        with self.assertRaises(ValidationError) as context:
            self.validator.validate_description(long_description)
        self.assertEqual(
            str(context.exception.detail[0]),
            "Описание не может превышать 1000 символов.",
        )

    def test_validate_description_valid(self):
        """
        Проверяет, что корректное описание не вызывает ошибок.
        """
        try:
            self.validator.validate_description("Valid description")
        except ValidationError:
            self.fail(
                "validate_description вызвал ValidationError для корректного описания."
            )

    def test_validate_image_invalid_format(self):
        """
        Проверяет, что изображение с недопустимым форматом вызывает ValidationError.
        """
        invalid_image = SimpleUploadedFile(
            "test.gif", b"file_content", content_type="image/gif"
        )
        with self.assertRaises(ValidationError) as context:
            self.validator.validate_image(invalid_image)
        self.assertEqual(
            str(context.exception.detail[0]),
            "Неподдерживаемый формат изображения. Допустимые форматы: JPG, JPEG, PNG, WEBP.",
        )

    def test_validate_image_too_large(self):
        """
        Проверяет, что изображение размером более 5 MB вызывает ValidationError.
        """
        large_image = SimpleUploadedFile(
            "test.jpg", b"a" * (5 * 1024 * 1024 + 1), content_type="image/jpeg"
        )
        with self.assertRaises(ValidationError) as context:
            self.validator.validate_image(large_image)
        self.assertEqual(
            str(context.exception.detail[0]),
            "Размер изображения не должен превышать 5MB.",
        )

    def test_validate_image_valid(self):
        """
        Проверяет, что корректное изображение не вызывает ошибок.
        """
        valid_image = SimpleUploadedFile(
            "test.jpg", b"file_content", content_type="image/jpeg"
        )
        try:
            self.validator.validate_image(valid_image)
        except ValidationError:
            self.fail(
                "validate_image вызвал ValidationError для корректного изображения."
            )

    def test_call_method_valid(self):
        """
        Проверяет, что метод __call__ корректно обрабатывает валидные данные.
        """
        data = {"title": "Valid title", "price": 1000}
        try:
            self.validator(data)
        except ValidationError:
            self.fail("__call__ вызвал ValidationError для валидных данных.")

    def test_call_method_invalid(self):
        """
        Проверяет, что метод __call__ корректно обрабатывает невалидные данные.
        """
        data = {"title": "", "price": -100}
        with self.assertRaises(ValidationError) as context:
            self.validator(data)
        self.assertEqual(
            str(context.exception.detail[0]),
            "Название товара обязательно для заполнения.",
        )
