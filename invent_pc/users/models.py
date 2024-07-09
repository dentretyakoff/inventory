from django.db import models


class StatusChoices(models.TextChoices):
    ACTIVE = 'active', 'Активен'
    INACTIVE = 'inactive', 'Неактивен'


class ADusers(models.Model):
    fio = models.TextField()
    adlogin = models.TextField()
    admail = models.TextField(blank=True)
    adgroup = models.TextField(blank=True)
    status = models.CharField(
        max_length=15,
        choices=StatusChoices.choices,
        default=StatusChoices.INACTIVE,
        verbose_name='Статус в AD',
    )
    rdlogin = models.ForeignKey(
        'Radius',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    vpn = models.ForeignKey(
        'VPN',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    def __str__(self):
        return f'{self.fio} ({self.adlogin})'


class Radius(models.Model):
    fio = models.TextField()
    rdlogin = models.TextField()
    status = models.CharField(
        max_length=15,
        choices=StatusChoices.choices,
        default=StatusChoices.INACTIVE,
        verbose_name='Статус в Radius',
    )

    def __str__(self):
        return f'{self.rdlogin}'


class VPN(models.Model):
    name = models.TextField()
    comment = models.TextField(blank=True)
    status = models.CharField(
        max_length=15,
        choices=StatusChoices.choices,
        default=StatusChoices.INACTIVE,
        verbose_name='Статус VPN',
    )

    def __str__(self):
        return f'{self.name}'
