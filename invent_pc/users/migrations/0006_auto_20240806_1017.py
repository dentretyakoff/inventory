# Generated by Django 3.2.16 on 2024-08-06 03:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_auto_20240731_1852'),
    ]

    operations = [
        migrations.AddField(
            model_name='gigrotermon',
            name='successfully_updated',
            field=models.BooleanField(default=True, help_text='Если информация об учетной записи не поступила при последнем обновлении, галочка снимается, запись можно удалить.', verbose_name='Успешно обновлена'),
        ),
        migrations.AlterField(
            model_name='adusers',
            name='successfully_updated',
            field=models.BooleanField(default=True, help_text='Если информация об учетной записи не поступила при последнем обновлении, галочка снимается, запись можно удалить.', verbose_name='Успешно обновлена'),
        ),
        migrations.AlterField(
            model_name='radius',
            name='successfully_updated',
            field=models.BooleanField(default=True, help_text='Если информация об учетной записи не поступила при последнем обновлении, галочка снимается, запись можно удалить.', verbose_name='Успешно обновлена'),
        ),
        migrations.AlterField(
            model_name='vpn',
            name='successfully_updated',
            field=models.BooleanField(default=True, help_text='Если информация об учетной записи не поступила при последнем обновлении, галочка снимается, запись можно удалить.', verbose_name='Успешно обновлена'),
        ),
    ]