from decimal import Decimal
from django.core.exceptions import ValidationError
from django.test import TestCase
from phonenumber_field.phonenumber import PhoneNumber
from rest_framework.exceptions import ErrorDetail
from rest_framework.test import APITestCase

from network_nodes.models import NetworkNode, Product
from network_nodes.serializers import NetworkNodeSerializer, ProductSerializer
from network_nodes.validators import NetworkNodeValidator


class NetworkNodeModelTest(TestCase):
    def setUp(self):
        self.factory = NetworkNode.objects.create(
            name="Factory 1",
            node_type=NetworkNode.FACTORY,
            email="factory1@example.com",
            country="Russia",
            city="Moscow",
            street="Lenina",
            house_number="1",
        )

    def test_create_factory(self):
        """Тестирование создания завода (уровень 0)"""
        self.assertEqual(self.factory.node_type, NetworkNode.FACTORY)
        self.assertEqual(self.factory.level, 0)
        self.assertIsNone(self.factory.supplier)
        self.assertEqual(self.factory.debt_to_supplier, Decimal('0.00'))

    def test_create_retail_with_supplier(self):
        """Тестирование создания розничной сети с поставщиком"""
        retail = NetworkNode.objects.create(
            name="Retail 1",
            node_type=NetworkNode.RETAIL,
            email="retail1@example.com",
            country="Russia",
            city="Moscow",
            street="Lenina",
            house_number="2",
            supplier=self.factory,
        )
        self.assertEqual(retail.node_type, NetworkNode.RETAIL)
        self.assertEqual(retail.level, 1)
        self.assertEqual(retail.supplier, self.factory)

    def test_create_individual_with_supplier(self):
        """Тестирование создания ИП с поставщиком"""
        retail = NetworkNode.objects.create(
            name="Retail 1",
            node_type=NetworkNode.RETAIL,
            email="retail1@example.com",
            country="Russia",
            city="Moscow",
            street="Lenina",
            house_number="2",
            supplier=self.factory,
        )
        individual = NetworkNode.objects.create(
            name="Individual 1",
            node_type=NetworkNode.INDIVIDUAL,
            email="individual1@example.com",
            country="Russia",
            city="Moscow",
            street="Lenina",
            house_number="3",
            supplier=retail,
        )
        self.assertEqual(individual.node_type, NetworkNode.INDIVIDUAL)
        self.assertEqual(individual.level, 2)
        self.assertEqual(individual.supplier, retail)




    def test_valid_hierarchy_levels(self):
        """Проверка допустимых уровней иерархии"""
        # Уровень 0 (завод)
        self.assertEqual(self.factory.level, 0)
        self.factory.full_clean()  # Не должно быть ошибок

        # Уровень 1 (розничная сеть)
        retail = NetworkNode.objects.create(
            name="Retail",
            node_type=NetworkNode.RETAIL,
            email="retail@example.com",
            country="Russia",
            city="Moscow",
            street="Lenina",
            house_number="1",
            supplier=self.factory,
        )
        self.assertEqual(retail.level, 1)
        retail.full_clean()  # Не должно быть ошибок

        # Уровень 2 (ИП)
        entrepreneur = NetworkNode.objects.create(
            name="Entrepreneur",
            node_type=NetworkNode.INDIVIDUAL,
            email="entrepreneur@example.com",
            country="Russia",
            city="Moscow",
            street="Lenina",
            house_number="2",
            supplier=retail,
        )
        self.assertEqual(entrepreneur.level, 2)
        entrepreneur.full_clean()  # Не должно быть ошибок


    def test_str_representation(self):
        """Тестирование строкового представления"""
        self.assertEqual(str(self.factory), "Завод: Factory 1")

    def test_repr_representation(self):
        """Тестирование repr представления"""
        repr_str = repr(self.factory)
        self.assertIn("NetworkNode(", repr_str)
        self.assertIn("name=Factory 1", repr_str)  # Без кавычек
        self.assertIn("node_type=factory", repr_str)
        self.assertIn("email=factory1@example.com", repr_str)


class ProductModelTest(TestCase):
    def setUp(self):
        self.factory = NetworkNode.objects.create(
            name="Factory 1",
            node_type=NetworkNode.FACTORY,
            email="factory1@example.com",
            country="Russia",
            city="Moscow",
            street="Lenina",
            house_number="1",
        )
        self.product = Product.objects.create(
            name="Smartphone",
            model="X100",
            release_date="2023-01-01",
            network_node=self.factory,
        )

    def test_create_product(self):
        """Тестирование создания продукта"""
        self.assertEqual(self.product.name, "Smartphone")
        self.assertEqual(self.product.model, "X100")
        self.assertEqual(str(self.product.release_date), "2023-01-01")
        self.assertEqual(self.product.network_node, self.factory)

    def test_str_representation(self):
        """Тестирование строкового представления продукта"""
        self.assertEqual(str(self.product), "Smartphone (X100)")

    def test_repr_representation(self):
        """Тестирование repr представления продукта"""
        self.assertIn("Product(", repr(self.product))
        self.assertIn("name='Smartphone'", repr(self.product))
        self.assertIn("model='X100'", repr(self.product))

    def test_unique_constraint(self):
        """Продукт с одинаковыми именем, моделью и звеном сети должен быть уникальным"""
        from django.core.exceptions import ValidationError

        # Создаем дубликат продукта
        duplicate_product = Product(
            name=self.product.name,
            model=self.product.model,
            release_date="2023-01-01",
            network_node=self.product.network_node,
        )

        # Проверяем валидацию
        with self.assertRaises(ValidationError) as context:
            duplicate_product.full_clean()

        # Проверяем точное сообщение об ошибке
        self.assertEqual(
            str(context.exception),
            "{'__all__': ['Продукт с такими значениями полей Звено сети, Название продукта и Модель продукта уже существует.']}"
        )


class NetworkNodeSerializerTest(APITestCase):
    def setUp(self):
        self.factory = NetworkNode.objects.create(
            name="Factory 1",
            node_type=NetworkNode.FACTORY,
            email="factory1@example.com",
            country="Russia",
            city="Moscow",
            street="Lenina",
            house_number="1",
        )
        self.valid_data = {
            "name": "Retail 1",
            "node_type": NetworkNode.RETAIL,
            "email": "retail1@example.com",
            "country": "Russia",
            "city": "Moscow",
            "street": "Lenina",
            "house_number": "2",
            "supplier": self.factory.id,
        }

    def test_valid_serializer(self):
        """Тестирование валидных данных"""
        serializer = NetworkNodeSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['name'], "Retail 1")
        self.assertEqual(serializer.validated_data['node_type'], NetworkNode.RETAIL)

    def test_missing_required_fields(self):
        """Тестирование отсутствия обязательных полей"""
        invalid_data = self.valid_data.copy()
        del invalid_data['name']
        serializer = NetworkNodeSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(
            serializer.errors['name'][0],
            ErrorDetail(string='Название звена сети обязательно.', code='required')
        )

    def test_invalid_node_type(self):
        """Тестирование невалидного типа звена"""
        invalid_data = self.valid_data.copy()
        invalid_data['node_type'] = 'invalid_type'
        serializer = NetworkNodeSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(
            str(serializer.errors['node_type'][0]),
            'Значения invalid_type нет среди допустимых вариантов.'
        )

    def test_read_only_fields(self):
        """Тестирование полей только для чтения"""
        data = self.valid_data.copy()
        data['level'] = 100  # Попытка изменить read-only поле
        serializer = NetworkNodeSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        # Убедимся, что read-only поле не входит в validated_data
        self.assertNotIn('level', serializer.validated_data)

    def test_update_removes_debt(self):
        """При обновлении debt_to_supplier должен быть удалён"""
        retail = NetworkNode.objects.create(
            name="Retail 1",
            node_type=NetworkNode.RETAIL,
            email="retail1@example.com",
            country="Russia",
            city="Moscow",
            street="Lenina",
            house_number="2",
            supplier=self.factory,
            debt_to_supplier=Decimal('100.00'),
        )
        data = {
            "name": "Retail Updated",
            "debt_to_supplier": "200.00",
        }
        serializer = NetworkNodeSerializer(instance=retail, data=data, partial=True)
        self.assertTrue(serializer.is_valid())
        updated_instance = serializer.save()
        self.assertEqual(updated_instance.name, "Retail Updated")
        self.assertEqual(updated_instance.debt_to_supplier, Decimal('100.00'))  # Не изменилось


class ProductSerializerTest(APITestCase):
    def setUp(self):
        self.factory = NetworkNode.objects.create(
            name="Factory 1",
            node_type=NetworkNode.FACTORY,
            email="factory1@example.com",
            country="Russia",
            city="Moscow",
            street="Lenina",
            house_number="1",
        )
        self.valid_data = {
            "name": "Smartphone",
            "model": "X100",
            "release_date": "2023-01-01",
            "network_node": self.factory.id,
        }

    def test_valid_serializer(self):
        """Тестирование валидных данных"""
        serializer = ProductSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['name'], "Smartphone")
        self.assertEqual(serializer.validated_data['model'], "X100")

    def test_missing_required_fields(self):
        """Тестирование отсутствия обязательных полей"""
        invalid_data = self.valid_data.copy()
        del invalid_data['name']
        serializer = ProductSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('name', serializer.errors)


from rest_framework.exceptions import ValidationError

class NetworkNodeValidatorTest(TestCase):
    def setUp(self):
        self.validator = NetworkNodeValidator()
        self.valid_data = {
            "name": "Valid Name",
            "node_type": NetworkNode.FACTORY,
            "email": "valid@example.com",
            "country": "Russia",
            "city": "Moscow",
            "house_number": "1",
        }

    def test_validate_name(self):
        """Тестирование валидации названия"""
        invalid_data = self.valid_data.copy()
        invalid_data['name'] = ""
        with self.assertRaises(ValidationError) as context:
            self.validator(invalid_data)
        self.assertEqual(
            str(context.exception.detail[0]),
            "Название звена сети должно содержать минимум 2 символа."
        )

    def test_validate_node_type(self):
        """Тестирование валидации типа звена"""
        invalid_data = self.valid_data.copy()
        invalid_data['node_type'] = "invalid_type"
        with self.assertRaises(ValidationError) as context:
            self.validator(invalid_data)
        self.assertEqual(
            str(context.exception.detail[0]),
            "Некорректный тип звена сети."
        )

    def test_validate_email(self):
        """Тестирование валидации email"""
        invalid_data = self.valid_data.copy()
        invalid_data['email'] = "invalid-email"
        with self.assertRaises(ValidationError) as context:
            self.validator(invalid_data)
        self.assertEqual(
            str(context.exception.detail[0]),
            "Некорректный email."
        )

    def test_validate_country(self):
        """Тестирование валидации страны"""
        invalid_data = self.valid_data.copy()
        invalid_data['country'] = ""
        with self.assertRaises(ValidationError) as context:
            self.validator(invalid_data)
        self.assertEqual(
            str(context.exception.detail[0]),
            "Страна обязательна для заполнения."
        )

    def test_validate_house_number(self):
        """Тестирование валидации номера дома"""
        invalid_data = self.valid_data.copy()
        invalid_data['house_number'] = ""
        with self.assertRaises(ValidationError) as context:
            self.validator(invalid_data)
        self.assertEqual(
            str(context.exception.detail[0]),
            "Номер дома обязателен для заполнения."
        )

    def test_validate_debt(self):
        """Тестирование валидации задолженности"""
        invalid_data = self.valid_data.copy()
        invalid_data['debt_to_supplier'] = "-100"
        with self.assertRaises(ValidationError) as context:
            self.validator(invalid_data)
        self.assertEqual(
            str(context.exception.detail[0]),
            "Задолженность не может быть отрицательной."
        )