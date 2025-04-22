from rest_framework.exceptions import ValidationError

from network_nodes.models import NetworkNode


class NetworkNodeValidator:
    """
    Валидатор для проверки бизнес-логики звена сети (NetworkNode).
    """

    def __call__(self, data: dict) -> None:
        # Для PATCH-запроса проверяем только переданные поля

        # Проверка названия
        if "name" in data:
            self.validate_name(data["name"])

        # Проверка типа звена
        if "node_type" in data:
            self.validate_node_type(data["node_type"])

        # Проверка email
        if "email" in data:
            self.validate_email(data["email"])


        # Проверка страны
        if "country" in data:
            self.validate_country(data["country"])

        # Проверка города
        if "city" in data:
            self.validate_city(data["city"])

        # Проверка улицы
        if "street" in data:
            self.validate_street(data["street"])

        # Проверка номера дома
        if "house_number" in data:
            self.validate_house_number(data["house_number"])

        # Проверка задолженности
        if "debt_to_supplier" in data:
            self.validate_debt(data["debt_to_supplier"])


    def validate_name(self, name: str) -> None:
        if not name or len(name.strip()) < 2:
            raise ValidationError("Название звена сети должно содержать минимум 2 символа.")

    def validate_node_type(self, node_type: str) -> None:
        if node_type not in dict(NetworkNode.NODE_TYPE_CHOICES):
            raise ValidationError("Некорректный тип звена сети.")

    def validate_email(self, email: str) -> None:
        if not email or "@" not in email:
            raise ValidationError("Некорректный email.")


    def validate_country(self, country: str) -> None:
        if not country or len(country.strip()) < 2:
            raise ValidationError("Страна обязательна для заполнения.")

    def validate_city(self, city: str) -> None:
        if not city or len(city.strip()) < 2:
            raise ValidationError("Город обязателен для заполнения.")

    def validate_street(self, street: str) -> None:
        # Необязательное поле, но если есть — не менее 2 символов
        if street and len(street.strip()) < 2:
            raise ValidationError("Название улицы должно содержать минимум 2 символа.")

    def validate_house_number(self, house_number: str) -> None:
        if not house_number or len(house_number.strip()) < 1:
            raise ValidationError("Номер дома обязателен для заполнения.")

    def validate_debt(self, debt) -> None:
        try:
            value = float(debt)
        except (ValueError, TypeError):
            raise ValidationError("Задолженность должна быть числом.")
        if value < 0:
            raise ValidationError("Задолженность не может быть отрицательной.")
