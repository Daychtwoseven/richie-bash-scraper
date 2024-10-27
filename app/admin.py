from django.contrib import admin
from . models import BusinessTypes, BusinessCategory, BusinessReviews, Business


admin.site.register(Business)
admin.site.register(BusinessTypes)
admin.site.register(BusinessCategory)
admin.site.register(BusinessReviews)