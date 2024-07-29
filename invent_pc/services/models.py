from django.db import models


class MySQLDatabase(models.Model):
    name = models.CharField(
        'Название',
        max_length=255,
        help_text='Произвольное название БД'
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
        help_text='Пользователь для подключения к БД'
    )
    password = models.CharField(
        'Пароль',
        max_length=255,
        help_text='Пароль для подключения к БД'
    )
    database = models.CharField(
        'Название БД',
        max_length=255
    )
    active = models.BooleanField(
        'Активна',
        help_text='Подключение происходит только к активным БД'
    )

    def __str__(self):
        return self.name

    def to_dict(self):
        return {
            'host': self.host,
            'port': self.port,
            'user': self.user,
            'password': self.password,
            'database': self.database,
        }

    class Meta:
        ordering = ('id',)
        verbose_name = 'БД Гигротермон'
        verbose_name_plural = 'БД Гигротермон'
