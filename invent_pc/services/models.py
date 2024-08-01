from cryptography.fernet import Fernet
from django.conf import settings
from django.db import models

from exceptions.services import EncryptionKeyMissingError


class BaseService(models.Model):
    """Базовая модель сервиса."""
    name = models.CharField(
        'Название',
        max_length=255,
        help_text='Произвольное название сервиса'
    )
    host = models.CharField(
        'Сервер',
        max_length=255,
        help_text='IP-адрес или dns-имя сервера'
    )
    port = models.IntegerField('Порт сервера')
    user = models.CharField(
        'Пользователь',
        max_length=255,
        help_text='Пользователь для подключения к сервису'
    )
    password = models.CharField(
        'Пароль',
        max_length=255,
        help_text='Пароль для подключения к сервису'
    )
    active = models.BooleanField(
        'Активен',
        help_text='Подключение происходит только к активному сервису'
    )

    def __str__(self):
        return self.name

    def __get_fernet(self):
        encryption_key = settings.ENCRYPTION_KEY
        if not encryption_key:
            raise EncryptionKeyMissingError(
                'ENCRYPTION_KEY не заполнен в .env')
        return Fernet(encryption_key)

    def encrypt_password(self, password):
        fernet = self.__get_fernet()
        encrypted_password = fernet.encrypt(password.encode())
        return encrypted_password.decode()

    def decrypt_password(self, encrypted_password):
        fernet = self.__get_fernet()
        decrypted_password = fernet.decrypt(encrypted_password.encode())
        return decrypted_password.decode()

    def save(self, *args, **kwargs):
        """Шифрование пароля перед сохранением."""
        if self.password and not self.password.startswith('gAAAAA'):
            self.password = self.encrypt_password(self.password)
        super().save(*args, **kwargs)

    def get_decrypted_password(self):
        """Возвращает расшифрованный пароль."""
        return self.decrypt_password(self.password)

    class Meta:
        abstract = True


class MySQLDatabase(BaseService):
    database = models.CharField(
        'Название БД',
        max_length=255
    )

    def to_dict(self):
        return {
            'host': self.host,
            'port': self.port,
            'user': self.user,
            'password': self.get_decrypted_password(),
            'database': self.database,
        }

    class Meta:
        ordering = ('id',)
        verbose_name = 'БД Гигротермон'
        verbose_name_plural = 'БД Гигротермон'
