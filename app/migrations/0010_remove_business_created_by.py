# Generated by Django 5.1 on 2024-10-26 11:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0009_business_hours_business_phone_business_thumbnail'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='business',
            name='created_by',
        ),
    ]
