from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField

NULLABLE = {"null": True, "blank": True}


class NetworkNode(models.Model):
    """
    Модель, представляющая звено сети по продаже электроники.
    """

    FACTORY = "factory"
    RETAIL = "retail"
    INDIVIDUAL = "individual"

    NODE_TYPE_CHOICES = [
        (FACTORY, "Завод"),
        (RETAIL, "Розничная сеть"),
        (INDIVIDUAL, "Индивидуальный предприниматель"),
    ]

    name = models.CharField(
        max_length=255,
        verbose_name="Название звена сети",
        help_text="Укажите название звена сети",
    )

    node_type = models.CharField(
        max_length=20,
        choices=NODE_TYPE_CHOICES,
        verbose_name="Тип звена",
        help_text="Укажите тип звена",
    )

    email = models.EmailField(
        verbose_name="Электронная почта", help_text="Укажите электронную почту"
    )
    phone = PhoneNumberField(
        **NULLABLE,
        unique=True,
        verbose_name="телефон для связи",
        help_text="укажите телефон",
    )

    country = models.CharField(
        max_length=100, verbose_name="Страна", help_text="Укажите страну"
    )

    city = models.CharField(
        max_length=100, verbose_name="Город", help_text="Укажите город"
    )

    street = models.CharField(
        max_length=100, verbose_name="Улица", help_text="Укажите улицу", blank=True
    )

    house_number = models.CharField(
        max_length=20, verbose_name="Номер дома", help_text="Укажите номер дома"
    )

    supplier = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        related_name="children",
        verbose_name="Поставщик",
        help_text="Предыдущее звено в сети",
        **NULLABLE,
    )

    debt_to_supplier = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal("0.00"))],
        verbose_name="Задолженность перед поставщиком",
        help_text="Задолженность в денежном выражении",
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Время создания")

    level = models.PositiveSmallIntegerField(
        default=0, editable=False, verbose_name="Уровень в иерархии"
    )

    def save(self, *args, **kwargs):
        """Автоматический расчет уровня иерархии при сохранении"""
        # только при создании нового объекта
        if not self.pk:
            if self.supplier is None:
                # завод
                self.level = 0
            else:
                self.level = self.supplier.level + 1
        super().save(*args, **kwargs)

    def clean(self):
        """
        Проверка бизнес-логики на уровне модели (для валидации в админ - панели)
        """

        # Завод не может иметь поставщика
        if self.node_type == self.FACTORY and self.supplier:
            raise ValidationError("Завод не может иметь поставщика")

        # Проверка циклических зависимостей
        if self.supplier and self.supplier.id == self.id:
            raise ValidationError("Объект не может быть своим собственным поставщиком")

        # Проверка на глубину иерархии
        if self.supplier and self.supplier.level >= 2:
            raise ValidationError("Максимальный уровень иерархии - 2")

    def __repr__(self) -> str:
        """Строковое представление объекта для разработки"""
        return f"""NetworkNode(
id={self.id},
name={self.name},
node_type={self.node_type},
email={self.email},
country={self.country},
city={self.city},
street={self.street},
house_number={self.house_number},
supplier={self.supplier_id if self.supplier else None},
debt_to_supplier={self.debt_to_supplier},
created_at={self.created_at},
level={self.level})"""

    def __str__(self):
        return f"{self.get_node_type_display()}: {self.name}"

    class Meta:
        verbose_name = "Звено сети"
        verbose_name_plural = "Звенья сети"
        ordering = ["-created_at"]


class Product(models.Model):
    """
    Модель продукта, связанного с конкретным звеном сети.
    """

    name = models.CharField(
        max_length=255,
        verbose_name="Название продукта",
        help_text="укажите название продукта",
    )
    model = models.CharField(
        max_length=255,
        verbose_name="Модель продукта",
        help_text="укажите модель продукта",
    )
    release_date = models.DateField(
        verbose_name="Дата выхода на рынок", help_text="укажите дату выхода на рынок"
    )
    network_node = models.ForeignKey(
        "network_nodes.NetworkNode",
        on_delete=models.CASCADE,
        related_name="products",
        verbose_name="Звено сети",
    )

    def __repr__(self):
        return (
            f"Product(id={self.id}, name='{self.name}', model='{self.model}', "
            f"release_date={self.release_date}, network_node_id={self.network_node_id})"
        )

    def __str__(self):
        return f"{self.name} ({self.model})"

    class Meta:
        verbose_name = "Продукт"
        verbose_name_plural = "Продукты"
        constraints = [
            models.UniqueConstraint(
                fields=["network_node", "name", "model"], name="unique_product_per_node"
            )
        ]
