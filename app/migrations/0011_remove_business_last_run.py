# Generated by Django 5.1 on 2024-10-26 11:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0010_remove_business_created_by'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='business',
            name='last_run',
        ),
    ]
