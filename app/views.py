import time

from django.db.models import Count
from selenium.webdriver.support.wait import WebDriverWait

from app.models import BusinessTypes, Business, BusinessCategories
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import render
from . locations import locations
from datetime import datetime
from app.update_data import UpdateData
from app.google_scraper import run_google_scraper


def index_page(request):
    try:
        """print((
            Business.objects
            .values('google_pid')  # Group by the 'google' field
            .annotate(count=Count('id'))  # Count occurrences
            .order_by('google_pid')  # Optional: order by the 'google' field
        ))"""
        context = {
            'types': BusinessTypes.objects.all(),
            'categories': BusinessCategories.objects.all(),
            'business': Business.objects.all()[0:10],
            'locations': locations
        }
        return render(request, 'app/index.html', context)
    except Exception as e:
        print(e)
        return JsonResponse({'statusMsg': 'error'}, status=404)


def search_page(request):
    try:
        category = request.GET.get('category')
        location = request.GET.get('location')

        page_number = 1 if not request.GET.get('page')  else request.GET.get('page')
        paginator = Paginator(Business.objects.filter(type__category_id=category, type__address=location), 20)
        context = {
            'types': BusinessTypes.objects.all(),
            'categories': BusinessCategories.objects.all(),
            'business': paginator.get_page(page_number),
            'locations': locations,
            'location': location,
            'category': BusinessCategories.objects.filter(id=category).first()
        }
        return render(request, 'app/index.html', context)

    except Exception as e:
        print(e)
        return JsonResponse({'statusMsg': 'error'}, status=404)


def google_scraper(request):
    try:
        run_google_scraper()
    except Exception as e:
        print(e)
        return JsonResponse({'statusMsg': 'error'}, status=404)


def yelp_scraper(request):
    try:
        UpdateData()
    except Exception as e:
        print(e)