# Generated by Django 3.2.16 on 2024-07-11 07:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Radius',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fio', models.CharField(max_length=200, verbose_name='ФИО')),
                ('login', models.CharField(max_length=100, unique=True, verbose_name='Логин в Radius')),
                ('status', models.CharField(choices=[('active', 'Активен'), ('inactive', 'Неактивен')], default='inactive', max_length=15, verbose_name='Статус в Radius')),
            ],
        ),
        migrations.CreateModel(
            name='VPN',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('login', models.CharField(max_length=50, unique=True, verbose_name='Логин VPN')),
                ('comment', models.TextField(blank=True, null=True, verbose_name='Комментарий')),
                ('status', models.CharField(choices=[('active', 'Активен'), ('inactive', 'Неактивен')], default='inactive', max_length=15, verbose_name='Статус VPN')),
            ],
        ),
        migrations.CreateModel(
            name='ADUsers',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fio', models.CharField(max_length=200, verbose_name='ФИО')),
                ('login', models.CharField(max_length=100, unique=True, verbose_name='Логин в AD')),
                ('email', models.EmailField(blank=True, max_length=254, null=True, verbose_name='Email')),
                ('status', models.CharField(choices=[('active', 'Активен'), ('inactive', 'Неактивен')], default='inactive', max_length=15, verbose_name='Статус в AD')),
                ('rdlogin', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='ad_user', to='users.radius', verbose_name='Учетная запись Radius')),
                ('vpn', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='ad_user', to='users.vpn', verbose_name='Учетная запись VPN')),
            ],
            options={
                'ordering': ('fio',),
            },
        ),
    ]
