# Generated by Django 5.1.4 on 2024-12-07 17:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('AppGDP', '0009_remove_sala_quantidade_itens'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sala',
            name='descricao',
            field=models.CharField(max_length=1500),
        ),
    ]
