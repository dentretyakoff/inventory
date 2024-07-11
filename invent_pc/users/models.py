from django.db import models


class StatusChoices(models.TextChoices):
    ACTIVE = 'active', 'Активен'
    INACTIVE = 'inactive', 'Неактивен'


class ADUsers(models.Model):
    fio = models.CharField('ФИО', max_length=200)
    login = models.CharField('Логин в AD', unique=True, max_length=100)
    email = models.EmailField('Email', blank=True, null=True)
    status = models.CharField(
        max_length=15,
        choices=StatusChoices.choices,
        default=StatusChoices.INACTIVE,
        verbose_name='Статус в AD',
    )
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

    def __str__(self):
        return f'{self.fio} ({self.login})'

    class Meta:
        ordering = ('fio',)


class Radius(models.Model):
    fio = models.CharField('ФИО', max_length=200)
    login = models.CharField('Логин в Radius', unique=True, max_length=100)
    status = models.CharField(
        max_length=15,
        choices=StatusChoices.choices,
        default=StatusChoices.INACTIVE,
        verbose_name='Статус в Radius',
    )

    def __str__(self):
        return f'{self.login}'

    class Meta:
        ordering = ('login',)


class VPN(models.Model):
    login = models.CharField('Логин VPN', unique=True, max_length=50)
    comment = models.TextField('Комментарий', blank=True, null=True)
    status = models.CharField(
        max_length=15,
        choices=StatusChoices.choices,
        default=StatusChoices.INACTIVE,
        verbose_name='Статус VPN',
    )

    def __str__(self):
        return f'{self.login}'

    class Meta:
        ordering = ('login',)
