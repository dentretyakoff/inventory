# Generated by Django 3.2.16 on 2023-10-03 04:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('comps', '0005_virtualmachine_vm_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hostvirtualmachine',
            name='vm',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='host_vm', to='comps.virtualmachine'),
        ),
    ]
