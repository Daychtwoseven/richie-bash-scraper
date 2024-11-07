from django.contrib.auth.models import User
from django.db import models
import uuid

from django.utils.text import slugify


class BusinessReviews(models.Model):
    sources_choices = [
        ('google', 'Google'),
        ('facebook', 'Facebook'),
        ('yelp', 'Yelp')
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    business = models.ForeignKey('Business', models.RESTRICT, null=True)
    content = models.JSONField()
    source = models.CharField(max_length=20, choices=sources_choices)


class BusinessCategories(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    slug = models.SlugField(blank=True)

    def __str__(self):
        return str(self.name)

    def save(self, *args, **kwargs):
        # Auto-generate the slug from the title if it is not provided
        if not self.slug:
            self.slug = slugify(self.name)  # Use Django's slugify method to create a slug
        super().save(*args, **kwargs)

    
class BusinessTypes(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category = models.ForeignKey(BusinessCategories, models.RESTRICT)
    address = models.CharField(max_length=255, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    last_run = models.DateTimeField(auto_now_add=False, blank=True, null=True)
    slug = models.SlugField(blank=True)

    def save(self, *args, **kwargs):
        # Auto-generate the slug from the title if it is not provided
        if not self.slug:
            self.slug = slugify(self.address)  # Use Django's slugify method to create a slug
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{str(self.category.name)} | {self.address}"


class Business(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    type = models.ForeignKey(BusinessTypes, models.RESTRICT)
    name = models.CharField(max_length=255, blank=True)
    description = models.TextField(null=True, blank=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True, blank=True)
    google_reviews_count = models.CharField(max_length=255,default=0, blank=True)
    facebook_reviews_count = models.CharField(max_length=255,default=0, blank=True)
    yelp_reviews_count = models.CharField(max_length=255,default=0, blank=True)
    google_rating = models.CharField(max_length=255, default=0, null=True, blank=True)
    facebook_rating = models.CharField(max_length=255, default=0, null=True, blank=True)
    yelp_rating = models.CharField(max_length=255, default=0, null=True, blank=True)
    google_pid = models.TextField(null=True, blank=True)
    facebook_pid = models.TextField(null=True, blank=True)
    facebook_url = models.TextField(null=True, blank=True)
    yelp_url = models.TextField(null=True, blank=True)
    last_update = models.DateTimeField(auto_now_add=False, blank=True, null=True)
    thumbnail = models.TextField(null=True, blank=True)
    phone = models.TextField(null=True, blank=True)
    hours = models.TextField(null=True, blank=True)
    google_id = models.TextField(null=True, blank=True)
    google_cid = models.TextField(null=True, blank=True)
    website = models.CharField(max_length=255, null=True, blank=True)
    position = models.IntegerField(default=0, blank=True)
    google_map = models.TextField(null=True, blank=True)
    email = models.CharField(max_length=255, null=True, blank=True)
    our_review = models.TextField(null=True, blank=True)
    our_rating = models.CharField(max_length=255, null=True, default=0, blank=True)
    featured = models.BooleanField(default=0)

    def __str__(self):
        return f"{str(self.name)} | {self.type.category.name} | {self.type.address}"

