import logging
from datetime import date

from django.core.management.base import BaseCommand
from network_nodes.models import NetworkNode, Product

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fill_db():
    logger.info("Заполнение базы тестовыми звеньями сети и продуктами...")

    # 1. Создаем заводы (уровень 0)
    factory = NetworkNode.objects.create(
        name="Завод Электроника",
        node_type=NetworkNode.FACTORY,
        email="factory@electronics.com",
        phone="+79990001111",
        country="Россия",
        city="Москва",
        street="Электрозаводская",
        house_number="1"
    )
    logger.info(f"Создан завод: {factory}")

    # 2. Розничная сеть (уровень 1, supplier=factory)
    retail = NetworkNode.objects.create(
        name="Сеть Магазинов Техно",
        node_type=NetworkNode.RETAIL,
        email="retail@techno.com",
        phone="+79990002222",
        country="Россия",
        city="Санкт-Петербург",
        street="Технологическая",
        house_number="10",
        supplier=factory,
        debt_to_supplier="100000.00"
    )
    logger.info(f"Создана розничная сеть: {retail}")

    # 3. Индивидуальный предприниматель (уровень 2, supplier=retail)
    individual = NetworkNode.objects.create(
        name="ИП Иванов",
        node_type=NetworkNode.INDIVIDUAL,
        email="ivanov@ip.com",
        phone="+79990003333",
        country="Россия",
        city="Казань",
        street="Предпринимательская",
        house_number="5",
        supplier=retail,
        debt_to_supplier="25000.00"
    )
    logger.info(f"Создан индивидуальный предприниматель: {individual}")

    # 4. Еще один магазин (уровень 1, supplier=factory)
    retail2 = NetworkNode.objects.create(
        name="ТехноМаркет",
        node_type=NetworkNode.RETAIL,
        email="shop@technomarket.com",
        phone="+79990004444",
        country="Россия",
        city="Новосибирск",
        street="Маркетная",
        house_number="7",
        supplier=factory,
        debt_to_supplier="50000.00"
    )
    logger.info(f"Создана розничная сеть: {retail2}")

    # 5. Продукты для каждого звена
    products = [
        Product.objects.create(
            name="Смартфон X1",
            model="X1-2024",
            release_date=date(2024, 3, 1),
            network_node=factory
        ),
        Product.objects.create(
            name="Ноутбук Pro",
            model="Pro-15",
            release_date=date(2023, 12, 15),
            network_node=retail
        ),
        Product.objects.create(
            name="Планшет Mini",
            model="Mini-8",
            release_date=date(2024, 1, 20),
            network_node=individual
        ),
        Product.objects.create(
            name="Телевизор UltraHD",
            model="UHD-55",
            release_date=date(2023, 11, 5),
            network_node=retail2
        ),
    ]
    for product in products:
        logger.info(f"Создан продукт: {product}")

    logger.info("База успешно заполнена!")

class Command(BaseCommand):
    help = 'Заполняет базу тестовыми данными для демонстрации'

    def handle(self, *args, **kwargs):
        fill_db()
