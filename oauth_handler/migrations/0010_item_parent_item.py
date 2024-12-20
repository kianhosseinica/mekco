# Generated by Django 5.0.6 on 2024-09-15 18:35

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('oauth_handler', '0009_item_weight'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='parent_item',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='variants', to='oauth_handler.item'),
        ),
    ]
