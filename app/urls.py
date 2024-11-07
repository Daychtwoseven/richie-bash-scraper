"""
URL configuration for main project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from .views import index_page, search_page, google_scraper, yelp_scraper, update_business_page, show_business_page, \
    business_list, featured_business, business_list_search, categories_list, types_list

urlpatterns = [
    path('', index_page, name='app-index-page'),
    path('search/', search_page, name='app-search-page'),
    path('run-google-scraper/', google_scraper, name='app-run-google-scraper'),
    path('run-yelp-scraper/', yelp_scraper, name='app-run-yelp-scraper'),
    path('update-business/<str:business_id>/', update_business_page, name='app-update-business-page'),
    path('show-business/<str:business_id>/', show_business_page, name='app-show-business-page'),
    path('business-list/', business_list, name='app-business-list-page'),
    path('business-list-search/<slug:category>/<slug:location>/', business_list_search, name='app-business-list-search-page'),
    path('featured-business/', featured_business, name='app-featured-business-page'),
    path('categories-list/', categories_list, name='app-categories-list-page'),
    path('types-list/', types_list, name='app-types-list-page'),
]
