# Generated by Django 5.1 on 2024-10-28 09:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0015_remove_businesstypes_created_by'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='BusinessCategory',
            new_name='BusinessCategories',
        ),
    ]