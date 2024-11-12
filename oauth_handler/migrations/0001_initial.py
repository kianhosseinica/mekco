# Generated by Django 5.0.6 on 2024-07-30 18:27

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Brand',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('customer_id', models.CharField(max_length=50)),
                ('first_name', models.CharField(blank=True, max_length=255)),
                ('last_name', models.CharField(blank=True, max_length=255)),
                ('title', models.CharField(blank=True, max_length=255)),
                ('company', models.CharField(blank=True, max_length=255)),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
                ('phone', models.CharField(blank=True, max_length=255, null=True)),
                ('address', models.TextField(blank=True)),
                ('archived', models.BooleanField(default=False)),
                ('create_time', models.DateTimeField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Quote',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quote_number', models.CharField(blank=True, max_length=255, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='TaxClass',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Vendor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category_id', models.IntegerField(unique=True)),
                ('name', models.CharField(max_length=255)),
                ('node_depth', models.IntegerField(default=0)),
                ('full_path_name', models.CharField(max_length=255)),
                ('left_node', models.IntegerField()),
                ('right_node', models.IntegerField()),
                ('create_time', models.DateTimeField()),
                ('last_modified', models.DateTimeField()),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='children', to='oauth_handler.category')),
            ],
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField()),
                ('system_sku', models.CharField(max_length=255)),
                ('manufacturer_sku', models.CharField(max_length=255, unique=True)),
                ('default_cost', models.DecimalField(decimal_places=2, max_digits=10)),
                ('average_cost', models.DecimalField(decimal_places=2, max_digits=10)),
                ('quantity_on_hand', models.IntegerField()),
                ('reorder_point', models.IntegerField(default=0, verbose_name='Reorder Point')),
                ('reorder_level', models.IntegerField(default=0, verbose_name='Reorder Level')),
                ('price_default', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('price_msrp', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('price_online', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('itemID', models.IntegerField(null=True, unique=True)),
                ('brand', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='oauth_handler.brand')),
                ('category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='oauth_handler.category')),
                ('tax_class', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='oauth_handler.taxclass')),
                ('vendor', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='oauth_handler.vendor')),
            ],
        ),
        migrations.CreateModel(
            name='ItemImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image_url', models.URLField()),
                ('image_path', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, null=True)),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='oauth_handler.item')),
            ],
        ),
        migrations.CreateModel(
            name='QuoteItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField(default=1)),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='oauth_handler.item')),
                ('quote', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='oauth_handler.quote')),
            ],
        ),
        migrations.CreateModel(
            name='PriceRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.DecimalField(decimal_places=5, default=0.0, max_digits=10)),
                ('currency', models.CharField(choices=[('USD', 'US Dollars'), ('CAD', 'Canadian Dollars')], max_length=3)),
                ('record_date', models.DateField(default=django.utils.timezone.now)),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='price_records', to='oauth_handler.item')),
                ('vendor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='oauth_handler.vendor')),
            ],
        ),
    ]
