# Generated by Django 3.2.16 on 2024-07-28 17:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='mysqldatabase',
            options={'ordering': ('id',), 'verbose_name': 'БД Гигротермон', 'verbose_name_plural': 'БД Гигротермон'},
        ),
    ]
