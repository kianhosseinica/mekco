# Generated by Django 5.1.2 on 2024-10-26 20:44

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ecommerce', '0018_order_order_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='cart',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ecommerce.cart'),
        ),
    ]
