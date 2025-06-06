# Generated by Django 4.2.2 on 2025-04-22 13:24

from decimal import Decimal

import django.core.validators
import django.db.models.deletion
import phonenumber_field.modelfields
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="NetworkNode",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        help_text="Укажите название звена сети",
                        max_length=255,
                        verbose_name="Название звена сети",
                    ),
                ),
                (
                    "node_type",
                    models.CharField(
                        choices=[
                            ("factory", "Завод"),
                            ("retail", "Розничная сеть"),
                            ("individual", "Индивидуальный предприниматель"),
                        ],
                        help_text="Укажите тип звена",
                        max_length=20,
                        verbose_name="Тип звена",
                    ),
                ),
                (
                    "email",
                    models.EmailField(
                        help_text="Укажите электронную почту",
                        max_length=254,
                        verbose_name="Электронная почта",
                    ),
                ),
                (
                    "phone",
                    phonenumber_field.modelfields.PhoneNumberField(
                        blank=True,
                        help_text="укажите телефон",
                        max_length=128,
                        null=True,
                        region=None,
                        unique=True,
                        verbose_name="телефон для связи",
                    ),
                ),
                (
                    "country",
                    models.CharField(
                        help_text="Укажите страну",
                        max_length=100,
                        verbose_name="Страна",
                    ),
                ),
                (
                    "city",
                    models.CharField(
                        help_text="Укажите город", max_length=100, verbose_name="Город"
                    ),
                ),
                (
                    "street",
                    models.CharField(
                        blank=True,
                        help_text="Укажите улицу",
                        max_length=100,
                        verbose_name="Улица",
                    ),
                ),
                (
                    "house_number",
                    models.CharField(
                        help_text="Укажите номер дома",
                        max_length=20,
                        verbose_name="Номер дома",
                    ),
                ),
                (
                    "debt_to_supplier",
                    models.DecimalField(
                        decimal_places=2,
                        default=0,
                        help_text="Задолженность в денежном выражении",
                        max_digits=15,
                        validators=[
                            django.core.validators.MinValueValidator(Decimal("0.00"))
                        ],
                        verbose_name="Задолженность перед поставщиком",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Время создания"
                    ),
                ),
                (
                    "level",
                    models.PositiveSmallIntegerField(
                        default=0, editable=False, verbose_name="Уровень в иерархии"
                    ),
                ),
                (
                    "supplier",
                    models.ForeignKey(
                        blank=True,
                        help_text="Предыдущее звено в сети",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="children",
                        to="network_nodes.networknode",
                        verbose_name="Поставщик",
                    ),
                ),
            ],
            options={
                "verbose_name": "Звено сети",
                "verbose_name_plural": "Звенья сети",
                "ordering": ["-created_at"],
            },
        ),
    ]
