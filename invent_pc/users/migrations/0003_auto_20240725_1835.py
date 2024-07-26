# Generated by Django 3.2.16 on 2024-07-25 11:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_auto_20240711_1554'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='adusers',
            options={'ordering': ('fio',), 'verbose_name': 'Пользователь AD', 'verbose_name_plural': 'Пользователи AD'},
        ),
        migrations.AlterModelOptions(
            name='radius',
            options={'ordering': ('login',), 'verbose_name': 'Пользователь WiFi', 'verbose_name_plural': 'Пользователи WiFi'},
        ),
        migrations.AlterModelOptions(
            name='vpn',
            options={'ordering': ('login',), 'verbose_name': 'Пользователь VPN', 'verbose_name_plural': 'Пользователи VPN'},
        ),
    ]