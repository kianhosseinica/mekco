# Generated by Django 5.1.3 on 2024-12-04 21:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ecommerce', '0020_order_total_with_hst_and_shipping'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderitem',
            name='packed',
            field=models.BooleanField(default=False),
        ),
    ]
