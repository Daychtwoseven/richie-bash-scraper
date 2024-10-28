from django.contrib.auth.models import User
from django.db import models
import uuid


class BusinessReviews(models.Model):
    sources_choices = [
        ('google', 'Google'),
        ('facebook', 'Facebook'),
        ('yelp', 'Yelp')
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    content = models.TextField()
    source = models.CharField(max_length=20, choices=sources_choices)


class BusinessCategories(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)

    def __str__(self):
        return str(self.name)

    
class BusinessTypes(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category = models.ForeignKey(BusinessCategories, models.RESTRICT)
    address = models.CharField(max_length=255)
    date_created = models.DateTimeField(auto_now_add=True)
    last_run = models.DateTimeField(auto_now_add=False, blank=True, null=True)

    def __str__(self):
        return f"{str(self.category.name)} | {self.address}"



class Business(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    type = models.ForeignKey(BusinessTypes, models.RESTRICT)
    name = models.CharField(max_length=255)
    description = models.TextField(null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    reviews = models.ManyToManyField(BusinessReviews)
    google_reviews_count = models.IntegerField(default=0)
    facebook_reviews_count = models.IntegerField(default=0)
    yelp_reviews_count = models.IntegerField(default=0)
    google_rating = models.CharField(max_length=255, default=0)
    facebook_rating = models.CharField(max_length=255, default=0)
    yelp_rating = models.CharField(max_length=255, default=0)
    google_pid = models.TextField(null=True)
    facebook_pid = models.TextField(null=True)
    yelp_url = models.TextField(null=True)
    last_update = models.DateTimeField(auto_now_add=False, blank=True, null=True)
    thumbnail = models.TextField(null=True)
    phone = models.TextField(null=True)
    hours = models.TextField(null=True)
    google_id = models.TextField(null=True)
    google_cid = models.TextField(null=True)
    website = models.CharField(max_length=255, null=True)
    position = models.IntegerField(default=0)

    def __str__(self):
        return f"{str(self.name)} | {self.type.category.name} | {self.type.address}"

