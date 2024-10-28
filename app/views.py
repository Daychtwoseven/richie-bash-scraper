from datetime import datetime

from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import render
from app.models import BusinessTypes, Business, BusinessCategories
from .utils import serpapi, serpapi_reviews
from . locations import locations


def index_page(request):
    try:
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
        print(page_number)
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


def run_google_scraper(request):
    try:
        today = datetime.now()
        for category in BusinessCategories.objects.all():
            for location in locations:
                if not BusinessTypes.objects.filter(category=category, address=location).first():
                    business_type = BusinessTypes.objects.create(category=category, address=location)
                    print(f"Running {business_type.category.name} {location}")
                    data = serpapi(business_type.category.name, location)

                    position = 1
                    for place in data:
                        rating = place['rating'] if 'rating' in place else ''
                        review = place['reviews'] if 'reviews' in place else 0
                        description = place['description'] if 'description' in place else ''
                        thumbnail = place['thumbnail'] if 'thumbnail' in place else ''
                        name = place['title'] if 'title' in place else ''
                        phone = place['phone'] if 'phone' in place else ''
                        address = place['address'] if 'address' in place else ''
                        hours = place['hours'] if 'hours' in place else ''
                        place_id = place['place_id'] if 'place_id' in place else ''
                        google_id = place['data_id'] if 'data_id' in place else ''
                        google_cid = place['data_cid'] if 'data_cid' in place else ''
                        website = place['website'] if 'website' in place else ''
                        if not Business.objects.filter(google_pid=place_id):
                            Business.objects.create(website=website, google_id=google_id, google_cid=google_cid, position=position, type=business_type, google_rating=rating, google_reviews_count=review, description=description, thumbnail=thumbnail, name=name, phone=phone, address=address, hours=hours, google_pid=place_id, last_update=today)
                        position += 1
                    business_type.last_run = datetime.now()
                    business_type.save()

        return JsonResponse({'statusMsg': 'success'})

    except Exception as e:
        print(e)
        return JsonResponse({'statusMsg': 'error'}, status=404)