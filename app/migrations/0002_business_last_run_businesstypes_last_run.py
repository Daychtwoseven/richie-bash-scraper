# Generated by Django 5.1 on 2024-10-25 07:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='business',
            name='last_run',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='businesstypes',
            name='last_run',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
