from datetime import datetime

from django.http import JsonResponse
from django.shortcuts import render
from app.models import BusinessTypes, Business, BusinessCategory
from .utils import serpapi, serpapi_reviews
from . locations import locations


def index_page(request):
    try:
        serpapi_reviews('17246260837168166768')
        context = {
            'types': BusinessTypes.objects.all(),
            'business': Business.objects.all()
        }
        return render(request, 'app/index.html', context)
    except Exception as e:
        print(e)
        return JsonResponse({'statusMsg': 'error'}, status=404)


def run_google_scraper(request):
    try:
        today = datetime.now()
        for category in BusinessCategory.objects.all():
            for location in locations:
                if not BusinessTypes.objects.filter(category=category, address=location).first():
                    business_type = BusinessTypes.objects.create(category=category, address=location)
                    print(f"Running {business_type.category.name} {location}")
                    data = serpapi(business_type.category.name, location)

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
                        position = place['position'] if 'position' in place else ''
                        website = place['website'] if 'website' in place else ''
                        if not Business.objects.filter(google_pid=place_id):
                            Business.objects.create(website=website, google_id=google_id, google_cid=google_cid, position=position, type=bussiness_type, google_rating=rating, google_reviews_count=review, description=description, thumbnail=thumbnail, name=name, phone=phone, address=address, hours=hours, google_pid=place_id, last_update=today)
                    business_type.last_run = datetime.now()
                    business_type.save()

        return JsonResponse({'statusMsg': 'success'})

    except Exception as e:
        print(e)
        return JsonResponse({'statusMsg': 'error'}, status=404)