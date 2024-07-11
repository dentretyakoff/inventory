import json

from django.core.management import BaseCommand
from django.conf import settings

from users.models import ADUsers, Radius, VPN


class Command(BaseCommand):
    """Менеджмент-команда для загрузки тестовых учетных записей."""
    help = 'Загрузить тестовые данные учетных записей'

    def handle(self, *args, **kwarg):
        data_dir = settings.BASE_DIR / 'test_data'
        ad_users_data = data_dir / 'test_ad_users.json'
        radius_users_data = data_dir / 'test_radius_users.json'
        vpn_users_data = data_dir / 'test_vpn_users.json'
        try:
            # Создание учетных записей из AD
            with open(ad_users_data, encoding='utf-8') as json_file:
                data = json.load(json_file)
                for ad_user_data in data:
                    ADUsers.objects.get_or_create(**ad_user_data)
            self.stdout.write(self.style.SUCCESS(
                'Пользователи AD загружены.'))

            # Создание учетных записей Radius
            with open(radius_users_data, encoding='utf-8') as json_file:
                data = json.load(json_file)
                for radius_user_data in data:
                    Radius.objects.get_or_create(**radius_user_data)
            self.stdout.write(self.style.SUCCESS(
                'Пользователи Radius загружены.'))

            # Создание учетных записей VPN
            with open(vpn_users_data, encoding='utf-8') as json_file:
                data = json.load(json_file)
                for vpn_user_data in data:
                    VPN.objects.get_or_create(**vpn_user_data)
            self.stdout.write(self.style.SUCCESS(
                'Пользователи VPN загружены.'))

        except Exception as e:
            print(f'Ошибка загрузки учетных записей пользователей: {e}')
