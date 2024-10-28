from django.contrib import admin
from . models import BusinessTypes, BusinessCategories, BusinessReviews, Business


admin.site.register(Business)
admin.site.register(BusinessTypes)
admin.site.register(BusinessCategories)
admin.site.register(BusinessReviews)