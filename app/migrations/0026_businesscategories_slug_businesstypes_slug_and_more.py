# Generated by Django 5.1 on 2024-11-07 15:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0025_business_featured'),
    ]

    operations = [
        migrations.AddField(
            model_name='businesscategories',
            name='slug',
            field=models.SlugField(blank=True),
        ),
        migrations.AddField(
            model_name='businesstypes',
            name='slug',
            field=models.SlugField(blank=True),
        ),
    ]