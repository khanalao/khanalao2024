# Generated by Django 5.0.6 on 2024-10-11 10:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('menu', '0006_alter_category_cat_name_alter_category_slug'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fooditem',
            name='food_title',
            field=models.CharField(max_length=100),
        ),
    ]
