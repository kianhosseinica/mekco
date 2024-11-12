# Generated by Django 5.0.6 on 2024-08-30 17:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ecommerce', '0015_remove_returnrequest_refund_hst_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='returnrequest',
            name='refund_hst',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
        migrations.AddField(
            model_name='returnrequest',
            name='refund_subtotal',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
        migrations.AddField(
            model_name='returnrequest',
            name='restocking_fee',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
    ]