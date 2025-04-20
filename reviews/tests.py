import json

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.test import APITestCase

from ads.models import Ad
from reviews.models import Review
from reviews.validators import ReviewValidator
from users.models import User


class ReviewTestCase(APITestCase):
    def setUp(self) -> None:
        # Создаем пользователя и объявление для тестов
        self.user = User.objects.create_user(
            email="test@example.com", password="testpass", is_active=True
        )
        self.ad = Ad.objects.create(title="Test Ad", price=1000, author=self.user)

        # Аутентифицируем клиент
        self.client.force_authenticate(user=self.user)

    def test_create_review(self):
        """
        Проверяет создание отзыва и корректность ответа.
        """
        data = {"text": "Great ad!", "ad": self.ad.id}

        url = reverse("reviews:review-create")

        response = self.client.post(
            url, data=json.dumps(data), content_type="application/json"
        )

        # 1 гипотеза
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # 2 гипотеза
        response_data = response.json()
        self.assertEqual(response_data["id"], 1)
        self.assertEqual(response_data["text"], "Great ad!")
        self.assertEqual(response_data["author"], self.user.id)
        self.assertEqual(response_data["ad"], self.ad.id)
        self.assertIn("createdAt", response_data)

        # 3 гипотеза - тест на то, что объект сохранен в БД
        review = Review.objects.get(text="Great ad!")
        self.assertEqual(review.author, self.user)
        self.assertEqual(review.ad, self.ad)

    def test_list_reviews(self):
        """
        Проверяет получение списка отзывов и их сортировку по дате создания (новые выше).
        """
        # Создаем два отзыва
        Review.objects.create(text="First review", author=self.user, ad=self.ad)
        Review.objects.create(text="Second review", author=self.user, ad=self.ad)

        url = reverse("reviews:review-list")
        response = self.client.get(url)

        # 1 гипотеза
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 2 гипотеза (структура ответа)
        response_data = response.json()

        # Проверяем количество отзывов в списке
        self.assertEqual(response_data["count"], 2)
        self.assertEqual(len(response_data["results"]), 2)

        # Проверяем содержимое первого отзыва (чем новее, тем выше)
        self.assertEqual(response_data["results"][0]["text"], "Second review")
        self.assertEqual(response_data["results"][0]["author"], self.user.id)
        self.assertEqual(response_data["results"][0]["ad"], self.ad.id)

        # Проверяем содержимое второго отзыва
        self.assertEqual(response_data["results"][1]["text"], "First review")
        self.assertEqual(response_data["results"][1]["author"], self.user.id)
        self.assertEqual(response_data["results"][1]["ad"], self.ad.id)

    def test_retrieve_review(self):
        """
        Проверяет получение одного отзыва.
        """
        review = Review.objects.create(text="Test review", author=self.user, ad=self.ad)

        url = reverse("reviews:review-retrieve", kwargs={"pk": review.pk})

        response = self.client.get(url)

        # 1 гипотеза
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 2 гипотеза (структура ответа)
        response_data = response.json()
        self.assertEqual(response_data["id"], review.id)
        self.assertEqual(response_data["text"], "Test review")
        self.assertEqual(response_data["author"], self.user.id)
        self.assertEqual(response_data["ad"], self.ad.id)

    def test_retrieve_nonexistent_review(self):
        """
        Проверяет обработку запроса к несуществующему отзыву.
        """
        url = reverse("reviews:review-retrieve", kwargs={"pk": 9999})
        response = self.client.get(url)

        # 1 гипотеза
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_patch_review(self):
        """
        Проверяет частичное обновление отзыва.
        """
        review = Review.objects.create(text="Old review", author=self.user, ad=self.ad)

        url = reverse("reviews:review-update", kwargs={"pk": review.pk})

        data = {"text": "Updated review"}

        response = self.client.patch(
            url, data=json.dumps(data), content_type="application/json"
        )

        # 1 гипотеза
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 2 гипотеза - проверка, что данные действительно обновились
        review.refresh_from_db()
        self.assertEqual(review.text, "Updated review")

        # 3 гипотеза - проверка содержимого ответа
        response_data = response.json()
        self.assertEqual(response_data["text"], "Updated review")
        self.assertEqual(response_data["author"], self.user.id)
        self.assertEqual(response_data["ad"], self.ad.id)

    def test_put_review(self):
        """
        Проверяет полное обновление отзыва.
        """
        review = Review.objects.create(text="Old review", author=self.user, ad=self.ad)

        url = reverse("reviews:review-update", kwargs={"pk": review.pk})

        data = {"text": "Completely updated review", "ad": self.ad.id}

        response = self.client.put(
            url, data=json.dumps(data), content_type="application/json"
        )

        # 1 гипотеза
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 2 гипотеза - проверка, что данные действительно обновились
        review.refresh_from_db()
        self.assertEqual(review.text, "Completely updated review")
        self.assertEqual(review.ad, self.ad)

        # 3 гипотеза - проверка содержимого ответа
        response_data = response.json()
        self.assertEqual(response_data["text"], "Completely updated review")
        self.assertEqual(response_data["author"], self.user.id)
        self.assertEqual(response_data["ad"], self.ad.id)

    def test_delete_review(self):
        """
        Проверяет удаление отзыва.
        """
        review = Review.objects.create(text="Test review", author=self.user, ad=self.ad)

        # Убедимся, что отзыв существует в базе данных
        self.assertTrue(Review.objects.filter(id=review.id).exists())

        # URL для удаления отзыва
        url = reverse("reviews:review-delete", kwargs={"pk": review.pk})

        # Отправляем DELETE-запрос
        response = self.client.delete(url)

        # Проверяем статус ответа
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Проверяем, что отзыв больше не существует в базе данных
        self.assertFalse(Review.objects.filter(id=review.id).exists())

    def test_review_repr(self):
        """
        Проверяет строковое представление объекта Review с помощью метода __repr__.
        """
        review = Review.objects.create(text="Test review", author=self.user, ad=self.ad)

        expected_repr = f"""Review(
text={review.text},
author={review.author},
ad={review.ad},
created_at={review.created_at})"""

        self.assertEqual(repr(review), expected_repr)

    def test_review_str(self):
        """
        Проверяет строковое представление объекта Review с помощью метода __str__.
        """
        review = Review.objects.create(text="Test review", author=self.user, ad=self.ad)

        expected_str = f"Отзыв от {self.user} на объявление '{self.ad.title}'"
        self.assertEqual(str(review), expected_str)

    def test_review_meta(self):
        """
        Проверяет мета-данные модели Review.
        """
        self.assertEqual(Review._meta.verbose_name, "Отзыв")
        self.assertEqual(Review._meta.verbose_name_plural, "Отзывы")
        self.assertEqual(Review._meta.ordering, ["-created_at"])


class ReviewValidatorTest(TestCase):
    def setUp(self):
        self.validator = ReviewValidator()

    def test_validate_text_empty(self):
        """
        Проверяет, что пустой текст вызывает ValidationError.
        """
        with self.assertRaises(ValidationError) as context:
            self.validator.validate_text("")
        self.assertEqual(
            str(context.exception.detail[0]), "Текст отзыва обязателен для заполнения."
        )

    def test_validate_text_too_short(self):
        """
        Проверяет, что текст менее 2 символов вызывает ValidationError.
        """
        with self.assertRaises(ValidationError) as context:
            self.validator.validate_text("a")
        self.assertEqual(
            str(context.exception.detail[0]),
            "Отзыв должен содержать минимум 2 символа.",
        )

    def test_validate_text_valid(self):
        """
        Проверяет, что корректный текст не вызывает ошибок.
        """
        try:
            self.validator.validate_text("Valid review text")
        except ValidationError:
            self.fail("validate_text вызвал ValidationError для корректного текста.")

    def test_validate_forbidden_words(self):
        """
        Проверяет, что текст с запрещенными словами вызывает ValidationError.
        """
        forbidden_words = ReviewValidator.FORBIDDEN_WORDS
        for word in forbidden_words:
            with self.assertRaises(ValidationError) as context:
                self.validator.validate_forbidden_words(f"This is a {word}.")
            self.assertEqual(
                str(context.exception.detail[0]),
                f"Текст отзыва содержит запрещенное слово: {word}.",
            )

    def test_validate_forbidden_words_valid(self):
        """
        Проверяет, что текст без запрещенных слов не вызывает ошибок.
        """
        try:
            self.validator.validate_forbidden_words("This is a valid review.")
        except ValidationError:
            self.fail(
                "validate_forbidden_words вызвал ValidationError для корректного текста."
            )

    def test_validate_text_length_too_long(self):
        """
        Проверяет, что текст длиннее MAX_TEXT_LENGTH вызывает ValidationError.
        """
        long_text = "a" * (ReviewValidator.MAX_TEXT_LENGTH + 1)
        with self.assertRaises(ValidationError) as context:
            self.validator.validate_text_length(long_text)
        self.assertEqual(
            str(context.exception.detail[0]),
            f"Текст отзыва не должен превышать {ReviewValidator.MAX_TEXT_LENGTH} символов.",
        )

    def test_validate_text_length_valid(self):
        """
        Проверяет, что текст допустимой длины не вызывает ошибок.
        """
        valid_text = "a" * ReviewValidator.MAX_TEXT_LENGTH
        try:
            self.validator.validate_text_length(valid_text)
        except ValidationError:
            self.fail(
                "validate_text_length вызвал ValidationError для текста допустимой длины."
            )

    def test_call_method_valid(self):
        """
        Проверяет, что метод __call__ корректно обрабатывает валидные данные.
        """
        data = {"text": "Valid review text"}
        try:
            self.validator(data)
        except ValidationError:
            self.fail("__call__ вызвал ValidationError для валидных данных.")

    def test_call_method_invalid(self):
        """
        Проверяет, что метод __call__ корректно обрабатывает невалидные данные.
        """
        data = {"text": "спам"}
        with self.assertRaises(ValidationError) as context:
            self.validator(data)
        self.assertEqual(
            str(context.exception.detail[0]),
            "Текст отзыва содержит запрещенное слово: спам.",
        )
