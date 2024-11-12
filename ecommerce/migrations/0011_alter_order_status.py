# Generated by Django 5.0.6 on 2024-08-26 18:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ecommerce', '0010_orderitem'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('preparing', 'Preparing'), ('ready_for_pickup', 'Ready for Pickup'), ('ready_for_shipping', 'Ready for Shipping'), ('shipped', 'Shipped'), ('delivered', 'Delivered'), ('cancelled', 'Cancelled'), ('complete', 'Complete')], default='preparing', max_length=20),
        ),
    ]
