import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')
import django
django.setup()

import time
from datetime import datetime
from urllib.parse import urlencode

import requests
from django.http import JsonResponse

from app.locations import locations
from app.models import BusinessCategories, BusinessTypes, Business
from app.utils import capsolver_api


def google_scraper(q, location):
    data = []
    try:
        pages = [0, 20, 40, 60, 80, 100, 120, 140, 160, 180, 200, 220, 240, 260, 280, 300, 320, 340, 360, 380, 400]
        site_key = '6LdhIq8UAAAAAO3N-yHHx5_vmutjCSQW47P4jLH1'
        query = urlencode({'q': f"{q} in {location}"})
        for i in range(0, 20):
            print(f"Running {q} {location} | Page: {pages[i]}")
            g_captcha = capsolver_api("https://serpapi.com/", site_key)
            url = f"https://serpapi.com/search.json?engine=google_local&{query}&google_domain=google.com&async=true&gRecaptchaResponse={g_captcha}&start={pages[i]}"
            headers = {
                'accept': 'application/json, text/javascript, */*; q=0.01',
                'accept-language': 'en-US,en;q=0.7',
                'cookie': '',
                'priority': 'u=1, i',
                'referer': '',
                'sec-ch-ua': '"Chromium";v="128", "Not;A=Brand";v="24", "Brave";v="128"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-origin',
                'sec-gpc': '1',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
                'x-csrf-token': '',
                'x-requested-with': 'XMLHttpRequest'
            }
            response = requests.request("GET", url, headers=headers, proxies={
                'http': 'http://customer-dmvteam:Chadix2023%23AI@dc.pr.oxylabs.io:10000',
                'https': 'http://customer-dmvteam:Chadix2023%23AI@dc.pr.oxylabs.io:10000'
            })
            time.sleep(2)
            response = requests.request("GET", response.json()['search_metadata']['json_endpoint'])
            if response.status_code == 200:
                temp_data = response.json()
                if 'local_results' in temp_data and len(temp_data['local_results']) > 0:
                    for row in temp_data['local_results']:
                        data.append(row)

                if 'error' in temp_data:
                    print("Exit")
                    break
        return data

    except Exception as e:
        print(f"An error occurred: {e}")
        return data


def run_google_scraper():
    try:
        today = datetime.now()
        for category in BusinessCategories.objects.all():
            for location in locations:
                if not BusinessTypes.objects.filter(category=category, address=location).first():
                    business_type = BusinessTypes.objects.create(category=category, address=location)
                    print(f"Running {business_type.category.name} {location}")
                    data = google_scraper(business_type.category.name, location)

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
                        google_map = f"https://www.google.com/maps?cid={place['place_id'] if 'place_id' in place else ''}"
                        if not Business.objects.filter(google_pid=place_id).first() and not Business.objects.filter(
                                name=name, address=address).first():
                            Business.objects.create(google_map=google_map, website=website, google_id=google_id,
                                                    google_cid=google_cid, position=position, type=business_type,
                                                    google_rating=rating, google_reviews_count=review,
                                                    description=description, thumbnail=thumbnail, name=name,
                                                    phone=phone, address=address, hours=hours, google_pid=place_id,
                                                    last_update=today)
                        position += 1
                    business_type.last_run = datetime.now()
                    business_type.save()

        return JsonResponse({'statusMsg': 'success'})

    except Exception as e:
        print(e)
        return JsonResponse({'statusMsg': 'error'}, status=404)


if __name__ == "__main__":
    run_google_scraper()