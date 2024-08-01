from typing import Any
from django.db import models

from services.models import MySQLDatabase


class StatusChoices(models.TextChoices):
    ACTIVE = 'active', 'Активен'
    INACTIVE = 'inactive', 'Неактивен'


class BaseUserMixin(models.Model):
    """Базовая модель учетных записей из внешних систем."""
    login = models.CharField('Логин', unique=True, max_length=100)
    status = models.CharField(
        max_length=15,
        choices=StatusChoices.choices,
        default=StatusChoices.INACTIVE,
        verbose_name='Статус',
    )
    successfully_updated = models.BooleanField(
        default=True,
        verbose_name='Успешна обновлена',
        help_text=('Если информация об учетной записи не поступила '
                   'при последнем обновлении, галочка снимается, '
                   'запись можно удалить.')
    )

    @classmethod
    def add_user_to_block(cls, login: str) -> None:
        if not hasattr(cls, '_users_to_block'):
            cls._users_to_block = []
        cls._users_to_block.append(login)

    @classmethod
    def get_users_to_block(cls) -> list[str]:
        if not hasattr(cls, '_users_to_block'):
            cls._users_to_block = []
        return cls._users_to_block

    @classmethod
    def clear_users_for_blocking(cls) -> None:
        if hasattr(cls, '_users_to_block'):
            cls._users_to_block.clear()

    def needs_update(self, user_data):
        """Добавляет всем учетным записям метод для проверки изменений.
        user_data - данные учетной записи полученные из внешней системы.
        """
        needs_update = False
        for key, value in user_data.items():
            if getattr(self, key) != value:
                setattr(self, key, value)
                needs_update = True
        return needs_update

    class Meta:
        abstract = True


class ADUsers(BaseUserMixin):
    fio = models.CharField('ФИО', max_length=200)
    email = models.EmailField('Email', blank=True, null=True)
    rdlogin = models.ForeignKey(
        'Radius',
        on_delete=models.SET_NULL,
        related_name='ad_user',
        null=True,
        blank=True,
        verbose_name='Учетная запись Radius'
    )
    vpn = models.ForeignKey(
        'VPN',
        on_delete=models.SET_NULL,
        related_name='ad_user',
        null=True,
        blank=True,
        verbose_name='Учетная запись VPN'
    )

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.cached_status = self.status

    def __str__(self):
        return f'{self.fio} ({self.login})'

    @property
    def is_blocked(self) -> str:
        """Проверяет был ли пользователь заблокирован."""
        return (self.cached_status == StatusChoices.ACTIVE
                and self.status == StatusChoices.INACTIVE)

    def save(self, *args: Any, **kwargs: Any) -> None:
        """Добавляет пользователей в список на блокировку
        если учетная запись была заблокирована."""
        if self.is_blocked:
            ADUsers.add_user_to_block(self)
        return super().save(*args, **kwargs)

    class Meta:
        ordering = ('fio',)
        verbose_name = 'Пользователь AD'
        verbose_name_plural = 'Пользователи AD'


class Radius(BaseUserMixin):
    fio = models.CharField('ФИО', max_length=200)

    def __str__(self):
        return self.login

    @classmethod
    def get_users_to_block(cls) -> list[str]:
        if not hasattr(cls, '_users_to_block'):
            cls._users_to_block = []
        ad_users = ADUsers.get_users_to_block()
        for ad_user in ad_users:
            if ad_user.rdlogin:
                radius_user = ad_user.rdlogin
                radius_user.status = StatusChoices.INACTIVE
                cls._users_to_block.append(radius_user)
        return cls._users_to_block

    class Meta:
        ordering = ('login',)
        verbose_name = 'Пользователь WiFi'
        verbose_name_plural = 'Пользователи WiFi'


class VPN(BaseUserMixin):
    comment = models.TextField('Комментарий', blank=True, null=True)

    def __str__(self):
        return self.login

    @classmethod
    def get_users_to_block(cls) -> list[str]:
        if not hasattr(cls, '_users_to_block'):
            cls._users_to_block = []
        ad_users = ADUsers.get_users_to_block()
        for ad_user in ad_users:
            if ad_user.vpn:
                vpn_user = ad_user.vpn
                vpn_user.status = StatusChoices.INACTIVE
                cls._users_to_block.append(vpn_user)
        return cls._users_to_block

    class Meta:
        ordering = ('login',)
        verbose_name = 'Пользователь VPN'
        verbose_name_plural = 'Пользователи VPN'


class Gigrotermon(BaseUserMixin):
    login = models.CharField('Логин', max_length=50)
    db = models.ForeignKey(
        MySQLDatabase,
        on_delete=models.CASCADE,
        verbose_name='БД Гигротермон',
    )
    gigro_id = models.IntegerField(
        'Гигро id',
        help_text='ID в БД Гигротермон'
    )
    ad_user = models.ForeignKey(
        ADUsers,
        verbose_name='Пользователь AD',
        on_delete=models.CASCADE,
        related_name='gigro',
        null=True,
        blank=True
    )

    def __str__(self):
        return self.login

    @classmethod
    def get_users_to_block(cls) -> list[str]:
        if not hasattr(cls, '_users_to_block'):
            cls._users_to_block = []
        return cls._users_to_block

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['login', 'db'],
                name='unique_login_db'
            )
        ]
        ordering = ('login',)
        verbose_name = 'Пользователь Гигротермон'
        verbose_name_plural = 'Пользователи Гигротермон'
