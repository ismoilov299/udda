# Generated by Django 4.2.8 on 2024-01-12 20:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bot_app', '0018_shop_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='latitude',
        ),
        migrations.RemoveField(
            model_name='order',
            name='longitude',
        ),
    ]
