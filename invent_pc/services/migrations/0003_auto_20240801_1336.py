# Generated by Django 3.2.16 on 2024-08-01 06:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0002_alter_mysqldatabase_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mysqldatabase',
            name='active',
            field=models.BooleanField(help_text='Подключение происходит только к активному сервису', verbose_name='Активен'),
        ),
        migrations.AlterField(
            model_name='mysqldatabase',
            name='name',
            field=models.CharField(help_text='Произвольное название сервиса', max_length=255, verbose_name='Название'),
        ),
        migrations.AlterField(
            model_name='mysqldatabase',
            name='password',
            field=models.CharField(help_text='Пароль для подключения к сервису', max_length=255, verbose_name='Пароль'),
        ),
        migrations.AlterField(
            model_name='mysqldatabase',
            name='user',
            field=models.CharField(help_text='Пользователь для подключения к сервису', max_length=255, verbose_name='Пользователь'),
        ),
    ]
