# Generated by Django 5.0.6 on 2024-09-19 16:14

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ecommerce', '0017_alter_cartitem_item'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='order_time',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]