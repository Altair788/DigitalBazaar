from rest_framework.exceptions import ValidationError


class ReviewValidator:
    """
    Валидатор для проверки бизнес-логики отзыва.
    """

    FORBIDDEN_WORDS = ["спам", "реклама", "оскорбление"]
    MAX_TEXT_LENGTH = 1000

    def __call__(self, data: dict[str, any]) -> None:
        # для реализации PATCH - запроса
        if "text" in data:
            text = data.get("text")
            self.validate_text(text)
            self.validate_forbidden_words(text)
            self.validate_text_length(text)

    def validate_text(self, text: str) -> None:
        """
        Проверка содержания отзыва
        Args:
            text(str): Название объявления

        Raises:
            ValidationError: Текст отзыва обязателен для заполнения.
                             Отзыв должен содержать минимум 2 символа.
        Returns:
            None
        """
        if not text:
            raise ValidationError("Текст отзыва обязателен для заполнения.")

        if len(text) < 2:
            raise ValidationError("Отзыв должен содержать минимум 2 символа.")

    def validate_forbidden_words(self, text: str) -> None:
        """
        Проверка на наличие запрещенных слов в тексте отзыва.
        """
        for word in self.FORBIDDEN_WORDS:
            if word in text.lower():
                raise ValidationError(
                    f"Текст отзыва содержит запрещенное слово: {word}."
                )

    def validate_text_length(self, text: str) -> None:
        """
        Проверка длины текста отзыва.
        """
        if len(text) > self.MAX_TEXT_LENGTH:
            raise ValidationError(
                f"Текст отзыва не должен превышать {self.MAX_TEXT_LENGTH} символов."
            )
