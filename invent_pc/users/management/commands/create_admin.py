import os

from django.contrib.auth import get_user_model
from django.core.management import BaseCommand


class Command(BaseCommand):
    """Создание админа."""
    help = 'Создание админа'

    def handle(self, *args, **kwarg):
        user_model = get_user_model()
        username = os.getenv('ADMIN_USER')
        password = os.getenv('ADMIN_PASSWORD')
        email = os.getenv('ADMIN_EMAIL')
        if not username or not password or not email:
            self.stdout.write(
                self.style.ERROR(
                    'Заполни данные для создания админа в файле .env'))
            return
        try:
            user_model.objects.get(username=username)
        except user_model.DoesNotExist:
            user_model.objects.create_superuser(
                username=username,
                password=password,
                email=email
            )
            self.stdout.write(
                self.style.SUCCESS('Создан админ.'))
