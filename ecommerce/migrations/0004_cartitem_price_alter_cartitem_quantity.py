# Generated by Django 5.0.6 on 2024-08-06 18:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ecommerce', '0003_pricingrule'),
    ]

    operations = [
        migrations.AddField(
            model_name='cartitem',
            name='price',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
        migrations.AlterField(
            model_name='cartitem',
            name='quantity',
            field=models.IntegerField(default=1),
        ),
    ]