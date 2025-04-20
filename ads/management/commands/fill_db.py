from django.core.management.base import BaseCommand

from ads.models import Ad
from reviews.models import Review
from users.models import User


class Command(BaseCommand):
    help = "Fill database with sample ads and reviews"

    def handle(self, *args, **options):
        # Создаем тестовых пользователей
        user1 = User.objects.create_user(
            email="user1@example.com",
            password="testpass123",
            first_name="Иван",
            last_name="Петров",
            phone="+79161234567",
            is_active=True,  # Устанавливаем активный статус
            role=User.ROLE_ADMIN,  # Назначаем роль администратора
        )

        user2 = User.objects.create_user(
            email="user2@example.com",
            password="testpass123",
            first_name="Мария",
            last_name="Сидорова",
            phone="+79167654321",
            is_active=True,  # Устанавливаем активный статус
            role=User.ROLE_USER,  # Назначаем роль пользователя
        )

        # Список тестовых объявлений
        ads_data = [
            {
                "title": "Продам ноутбук Apple MacBook Pro",
                "price": 150000,
                "description": "Отличное состояние, 2023 года выпуска",
                "author": user1,
            },
            {
                "title": "Сдам 2-комнатную квартиру",
                "price": 35000,
                "description": "Центр города, свежий ремонт",
                "author": user2,
            },
            {
                "title": "Продам велосипед горный",
                "price": 25000,
                "description": "Пробег 200 км, идеальное состояние",
                "author": user1,
            },
        ]

        # Создаем объявления
        ads = []
        for ad_data in ads_data:
            ads.append(Ad.objects.create(**ad_data))

        # Список тестовых отзывов
        reviews_data = [
            {
                "text": "Отличный ноутбук, всё работает идеально!",
                "author": user2,
                "ad": ads[0],
            },
            {
                "text": "Дороговато, но качество того стоит",
                "author": user1,
                "ad": ads[0],
            },
            {"text": "Квартира соответствует описанию", "author": user1, "ad": ads[1]},
            {"text": "Велосипед как новый, рекомендую!", "author": user2, "ad": ads[2]},
        ]

        # Создаем отзывы
        Review.objects.bulk_create(
            [Review(**review_data) for review_data in reviews_data]
        )

        # Вывод информации о созданных пользователях
        self.stdout.write(self.style.SUCCESS("Созданные пользователи:"))
        users = User.objects.all()
        for user in users:
            role = "Администратор" if user.role == User.ROLE_ADMIN else "Пользователь"
            self.stdout.write(f"- {user.email} ({role})")

        # Вывод статистики по созданным данным
        self.stdout.write(self.style.SUCCESS("\nУспешно создано:"))
        self.stdout.write(self.style.SUCCESS(f"- {User.objects.count()} пользователей"))
        self.stdout.write(self.style.SUCCESS(f"- {Ad.objects.count()} объявлений"))
        self.stdout.write(self.style.SUCCESS(f"- {Review.objects.count()} отзывов"))
