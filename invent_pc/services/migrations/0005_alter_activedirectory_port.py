# Generated by Django 3.2.16 on 2024-08-01 14:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0004_activedirectory'),
    ]

    operations = [
        migrations.AlterField(
            model_name='activedirectory',
            name='port',
            field=models.IntegerField(help_text='389 - без ssl, 636 - ssl', verbose_name='Порт сервера'),
        ),
    ]
