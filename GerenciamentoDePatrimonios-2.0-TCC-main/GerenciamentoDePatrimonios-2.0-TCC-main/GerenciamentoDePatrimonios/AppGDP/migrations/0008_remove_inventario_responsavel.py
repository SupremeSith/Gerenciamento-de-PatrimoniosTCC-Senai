# Generated by Django 5.1.3 on 2024-11-25 01:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('AppGDP', '0007_alter_inventario_status_localizacao'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='inventario',
            name='responsavel',
        ),
    ]
