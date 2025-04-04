# Generated by Django 4.1.4 on 2023-02-27 13:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot_app', '0005_user_last_name'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='about',
            options={'verbose_name': 'О нас', 'verbose_name_plural': 'О нас'},
        ),
        migrations.AlterModelOptions(
            name='category',
            options={'verbose_name': 'Категории', 'verbose_name_plural': 'Категории'},
        ),
        migrations.AlterModelOptions(
            name='comment',
            options={'verbose_name': 'Комментарии', 'verbose_name_plural': 'Комментарии'},
        ),
        migrations.AlterModelOptions(
            name='new',
            options={'verbose_name': 'Новости', 'verbose_name_plural': 'Новости'},
        ),
        migrations.AlterModelOptions(
            name='product',
            options={'verbose_name': 'Продукты', 'verbose_name_plural': 'Продукты'},
        ),
        migrations.AlterModelOptions(
            name='user',
            options={'verbose_name': 'Клиенты', 'verbose_name_plural': 'Клиенты'},
        ),
        migrations.AddField(
            model_name='product',
            name='p_id',
            field=models.PositiveIntegerField(null=True),
        ),
    ]
