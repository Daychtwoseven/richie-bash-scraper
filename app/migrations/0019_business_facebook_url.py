# Generated by Django 4.0.10 on 2024-10-30 05:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0018_remove_business_reviews_businessreviews_business'),
    ]

    operations = [
        migrations.AddField(
            model_name='business',
            name='facebook_url',
            field=models.TextField(null=True),
        ),
    ]