from cryptography.fernet import Fernet

from django.core.management import BaseCommand


class Command(BaseCommand):
    """Генерация ключа для шифрования паролей."""
    help = 'Генерация ключа для шифрования паролей'

    def handle(self, *args, **kwarg):
        key = Fernet.generate_key()
        self.stdout.write(
                self.style.SUCCESS(key.decode()))
