# Generated by Django 5.1 on 2024-10-25 23:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_business_last_run_businesstypes_last_run'),
    ]

    operations = [
        migrations.AddField(
            model_name='business',
            name='address',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
