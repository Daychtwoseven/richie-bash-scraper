# Generated by Django 5.1 on 2024-10-30 17:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0020_alter_business_facebook_reviews_count_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='business',
            name='google_map',
            field=models.TextField(null=True),
        ),
    ]