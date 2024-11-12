# Generated by Django 5.0.6 on 2024-08-05 12:45

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ecommerce', '0002_remove_cart_items_cart_completed'),
        ('oauth_handler', '0004_rename_customer_customerlightspeed'),
    ]

    operations = [
        migrations.CreateModel(
            name='PricingRule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('customer_type', models.CharField(choices=[('bronze', 'Bronze'), ('gold', 'Gold'), ('hvac', 'HVAC'), ('individual', 'Individual'), ('platinum', 'Platinum'), ('silver', 'Silver'), ('supplier', 'Supplier')], max_length=50)),
                ('discount_percentage', models.DecimalField(decimal_places=2, max_digits=5)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='oauth_handler.category')),
            ],
        ),
    ]