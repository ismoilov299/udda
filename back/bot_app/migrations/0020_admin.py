# Generated by Django 4.2.8 on 2024-01-12 21:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot_app', '0019_remove_order_latitude_remove_order_longitude'),
    ]

    operations = [
        migrations.CreateModel(
            name='Admin',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.IntegerField(unique=True)),
                ('name', models.CharField(blank=True, max_length=100, null=True)),
                ('delivery_right', models.BooleanField(default=False)),
                ('stat_right', models.BooleanField(default=False)),
                ('report_right', models.BooleanField(default=False)),
                ('test_right', models.BooleanField(default=False)),
                ('all_right', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name': 'admins',
                'verbose_name_plural': 'admins',
            },
        ),
    ]
