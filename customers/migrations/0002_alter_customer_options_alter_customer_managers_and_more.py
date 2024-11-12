# Generated by Django 5.0.6 on 2024-07-30 22:23

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('customers', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='customer',
            options={},
        ),
        migrations.AlterModelManagers(
            name='customer',
            managers=[
            ],
        ),
        migrations.RemoveField(
            model_name='customer',
            name='addresses',
        ),
        migrations.RemoveField(
            model_name='customer',
            name='date_joined',
        ),
        migrations.RemoveField(
            model_name='customer',
            name='username',
        ),
        migrations.AddField(
            model_name='customer',
            name='additional_emails',
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.AlterField(
            model_name='customer',
            name='email',
            field=models.EmailField(max_length=254, unique=True),
        ),
        migrations.AlterField(
            model_name='customer',
            name='first_name',
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AlterField(
            model_name='customer',
            name='groups',
            field=models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups'),
        ),
        migrations.AlterField(
            model_name='customer',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='customer',
            name='is_staff',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='customer',
            name='last_name',
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AlterField(
            model_name='customer',
            name='user_permissions',
            field=models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions'),
        ),
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('street', models.CharField(max_length=255)),
                ('city', models.CharField(max_length=100)),
                ('province', models.CharField(max_length=100)),
                ('postal_code', models.CharField(max_length=20)),
                ('country', models.CharField(max_length=100)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='addresses', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]