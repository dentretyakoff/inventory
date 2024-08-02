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

    def credentials(self):
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


class ActiveDirectory(BaseService):
    port = models.IntegerField(
        'Порт сервера',
        help_text='389 - без ssl, 636 - ssl'
    )
    base_dn = models.CharField(
        'Базовое уникальное имя',
        max_length=300,
        help_text='В каком OU искать пользователей'
    )
    seatch_filter = models.CharField(
        'Фильтр',
        max_length=300,
        help_text='Позволяет искать объекты определенного типа'
    )

    def credentials(self):
        return {
            'host': self.host,
            'port': self.port,
            'user': self.user,
            'password': self.get_decrypted_password(),
        }

    class Meta:
        ordering = ('id',)
        verbose_name = 'ActiveDirectory'
        verbose_name_plural = 'ActiveDirectory'


class Mikrotik(BaseService):
    port = models.IntegerField(
        'Порт сервера',
        help_text='8728 - без ssl, 8729 - ssl'
    )
    use_ssl = models.BooleanField('Использовать SSL')
    ssl_verify = models.BooleanField('Проверять сертификат')
    ssl_verify_hostname = models.BooleanField(
        'Проверять dns-имя сервера',
        help_text='Проверять dns-имя сервера с CN в сертификате'
    )
    need_disable = models.BooleanField('Блокировать учетные записи')

    def credentials(self):
        return {
            'host': self.host,
            'port': self.port,
            'user': self.user,
            'password': self.get_decrypted_password(),
            'use_ssl': self.use_ssl,
            'ssl_verify': self.ssl_verify,
            'ssl_verify_hostname': self.ssl_verify_hostname
        }

    class Meta:
        ordering = ('id',)
        verbose_name = 'Mikrotik'
        verbose_name_plural = 'Mikrotik'


class RadiusServer(BaseService):
    host = models.CharField(
        'Сервер',
        max_length=255,
        help_text=('IP-адрес или dns-имя сервера, пример: '
                   '"http://inventory.yourdomen.org:5985/wsman" или '
                   '"https://inventory.yourdomen.org:5986/wsman"')
    )
    port = None
    read_users_ps_script = models.TextField(
        'Скрипт чтения пользователей',
        help_text='Должен вернуть json строку'
    )
    cert_validation = models.BooleanField('Проверять сертификат')
    need_disable = models.BooleanField('Блокировать учетные записи')

    def credentials(self):
        return {
            'host': self.host,
            'user': self.user,
            'password': self.get_decrypted_password(),
            'cert_validation': self.cert_validation
        }

    class Meta:
        ordering = ('id',)
        verbose_name = 'Radius'
        verbose_name_plural = 'Radius'
