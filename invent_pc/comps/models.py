from datetime import datetime, timedelta

from django.db import models
from django.utils import timezone
from django.conf import settings


class ItemsChoices(models.TextChoices):
    LOST = 'lost', 'Потерян'
    INSTALLED = 'installed', 'Установлен'
    UNINSTALLED = 'uninstalled', 'Снят'


class Disk(models.Model):
    model = models.CharField('Модель', max_length=100)
    install_date = models.DateTimeField(
        'Дата установки', auto_now_add=True
    )
    uninstall_date = models.DateTimeField('Дата снятия',
                                          null=True,
                                          blank=True,
                                          default=None)
    capacity = models.CharField('Объем, Гб.', max_length=20)
    serial_number = models.CharField(
        'Серийный номер',
        max_length=100,
        null=True,
        blank=True,
        default='Отсутствует')
    comp = models.ForeignKey('Comp',
                             related_name='disks',
                             on_delete=models.CASCADE,
                             null=True,
                             blank=True)
    status = models.CharField(
        max_length=15,
        choices=ItemsChoices.choices,
        default=ItemsChoices.INSTALLED,
        verbose_name='Статус диска',
    )

    def __str__(self):
        return f'{self.capacity} GB'

    class Meta:
        ordering = ['uninstall_date']


class Ram(models.Model):
    model = models.CharField('Модель', max_length=100)
    install_date = models.DateTimeField(
        'Дата установки', auto_now_add=True
    )
    uninstall_date = models.DateTimeField(
        'Дата снятия',
        null=True,
        blank=True,
        default=None)
    capacity = models.CharField('Объем, Гб.', max_length=20)
    serial_number = models.CharField(
        'Серийный номер',
        max_length=100,
        null=True,
        blank=True,
        default='Отсутствует')
    comp = models.ForeignKey(
        'Comp',
        related_name='rams',
        on_delete=models.CASCADE,
        null=True,
        blank=True)
    status = models.CharField(
        max_length=15,
        choices=ItemsChoices.choices,
        default=ItemsChoices.INSTALLED,
        verbose_name='Статус модуля памяти',
    )

    def __str__(self):
        return f'{self.capacity} GB'

    class Meta:
        ordering = ['uninstall_date']


class Monitor(models.Model):
    model = models.CharField('Модель', max_length=100)
    install_date = models.DateTimeField(
        'Дата установки', auto_now_add=True
    )
    uninstall_date = models.DateTimeField(
        'Дата снятия',
        null=True,
        blank=True,
        default=None)
    manufacturer = models.CharField('Производитель', max_length=50)
    serial_number = models.CharField(
        'Серийный номер',
        max_length=100,
        null=True,
        blank=True,
        default='Отсутствует')
    comp = models.ForeignKey(
        'Comp',
        related_name='monitors',
        on_delete=models.CASCADE,
        null=True,
        blank=True)
    status = models.CharField(
        max_length=15,
        choices=ItemsChoices.choices,
        default=ItemsChoices.INSTALLED,
        verbose_name='Статус',
    )

    def __str__(self):
        return f'{self.manufacturer} {self.model}'

    class Meta:
        ordering = ['uninstall_date']


class WebCamera(models.Model):
    model = models.CharField('Модель', max_length=100, unique=True)

    def __str__(self):
        return self.model


class Department(models.Model):
    "Отделы в которых расположены компьютеры."
    name = models.CharField('Департамент', max_length=200, unique=True)

    def __str__(self) -> str:
        return self.name


class Comp(models.Model):
    pc_name = models.CharField('Имя ПК', max_length=100)
    add_date = models.DateTimeField(
        'Дата добавления', auto_now_add=True
    )
    online_date = models.DateTimeField(
        'Дата последнего подключения',
        default=datetime(2000, 1, 1)
    )
    win_ver = models.CharField('Версия ОС', max_length=100)
    os_arch = models.CharField('Архитектура', max_length=20)
    cpu = models.CharField('Процессор', max_length=50)
    motherboard = models.CharField('Материнская плата', max_length=100)
    department = models.ForeignKey(Department,
                                   related_name='comp',
                                   on_delete=models.CASCADE)
    web_camera = models.ForeignKey(WebCamera,
                                   related_name='comp',
                                   on_delete=models.CASCADE)

    def is_offline_long_time(self):
        """Определение компьютеров с большим офлайн периодом, для удаления."""
        six_months_ago = timezone.now() - timedelta(days=settings.DAYS_OFFLINE)
        return self.online_date < six_months_ago

    def __str__(self):
        return self.pc_name

    class Meta:
        ordering = ['-add_date']


class Host(models.Model):
    """Хосты с гипервизорами."""
    name = models.CharField('Имя хоста', max_length=100)
    vms = models.ManyToManyField('VirtualMachine',
                                 verbose_name='Виртуальные машины',
                                 through='HostVirtualMachine')


class VirtualMachine(models.Model):
    """Виртуальные машины."""
    name = models.CharField('Имя виртуальной машины', max_length=100)
    uptime = models.DurationField(default=timedelta(seconds=1))
    vm_id = models.CharField('ID виртуальной машины',
                             max_length=100,
                             default='Не определен')

    class Meta:
        ordering = ['name']


class HostVirtualMachine(models.Model):
    "Связь виртуальных машин с хостами."
    host = models.ForeignKey('Host',
                             on_delete=models.CASCADE,
                             related_name='host_vm')
    vm = models.ForeignKey('VirtualMachine',
                           on_delete=models.CASCADE,
                           related_name='host_vm')


class VMAdapter(models.Model):
    """Сетевые адаптеры виртуальных машин."""
    mac = models.CharField('Мак-адрес', max_length=50)
    vlan = models.IntegerField('VlanID')
    vm = models.ForeignKey(VirtualMachine,
                           related_name='adapter',
                           on_delete=models.CASCADE)

    def is_duplicate(self):
        """Метод для определения дубликатов мак-адресов."""
        count_mac = VMAdapter.objects.filter(mac=self.mac).count()
        return count_mac > settings.COUNT_MAC
