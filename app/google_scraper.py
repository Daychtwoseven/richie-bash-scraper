import os
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from urllib.parse import urlencode

import requests
from django.http import JsonResponse

from app.locations import locations
from app.models import BusinessCategories, BusinessTypes, Business
from app.utils import capsolver_api, find_closest_offset


def google_scraper_s2(q, location, business_type):
    data = []
    try:
        session = requests.Session()
        businesses = Business.objects.filter(type=business_type).count()
        offset = find_closest_offset(businesses)
        print(f"Current offset count {businesses} | Result: {offset}")
        pages = [0, 20, 40, 60, 80, 100, 120, 140, 160, 180, 200, 220, 240, 260, 280, 300, 320, 340, 360, 380, 400]
        site_key = '6LdhIq8UAAAAAO3N-yHHx5_vmutjCSQW47P4jLH1'
        query = urlencode({'q': f"{q.lower()} in {location}"})
        for i in range(pages.index(offset), 20):
            print(f"Running {q} {location} | Page: {pages[i]}")
            g_captcha = capsolver_api("https://serpapi.com/", site_key)
            url = f"https://serpapi.com/search.json?engine=google_local&{query}&google_domain=google.com&start={pages[i]}&async=true&gRecaptchaResponse={g_captcha}"
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
            response = session.request("GET", url, headers=headers)
            temp_json_data = response.json()
            if 'organic_results' not in temp_json_data and 'search_metadata' in temp_json_data and 'json_endpoint' in \
                    temp_json_data['search_metadata']:
                time.sleep(2)
                response = session.request("GET", response.json()['search_metadata']['json_endpoint'])

            if response.status_code == 200:
                temp_data = response.json()
                if 'local_results' in temp_data and len(temp_data['local_results']) > 0:
                    for row in temp_data['local_results']:
                        data.append(row)

                if 'error' in temp_data:
                    print(temp_data)
                    print("Exit")
                    break
        return data

    except Exception as e:
        print(f"An error occurred: {e}")
        return data


def google_scraper_s1(category, location):
    try:
        today = datetime.now()
        business_type_checker = BusinessTypes.objects.filter(category=category, address=location).first()
        business_type = BusinessTypes.objects.create(category=category, address=location) if not business_type_checker else business_type_checker
        print(f"Running {business_type.category.name} {location}")
        data = google_scraper_s2(business_type.category.name, location, business_type)

        print(len(data))
        for place in data:
            position = place['position'] if 'position' in place else ''
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
            Business.objects.create(google_map=google_map, website=website, google_id=google_id,
                                    google_cid=google_cid, position=position, type=business_type,
                                    google_rating=rating, google_reviews_count=review,
                                    description=description, thumbnail=thumbnail, name=name,
                                    phone=phone, address=address, hours=hours, google_pid=place_id,
                                    last_update=today)
        business_type.last_run = datetime.now()
        business_type.save()

        return JsonResponse({'statusMsg': 'success'})

    except Exception as e:
        print(e)
        return JsonResponse({'statusMsg': 'error'}, status=404)


def run_google_scraper():
    try:
        category = BusinessCategories.objects.first()
        with ThreadPoolExecutor(max_workers=100) as executor:
            # Submit tasks to the executor
            futures = {executor.submit(google_scraper_s1, category, location): location for location in locations}

            # Collect results as they complete
            for future in futures:
                try:
                    result = future.result()  # This will block until the result is available
                except Exception as e:
                    print(f"Error processing item {futures[future]}: {str(e)}")

        return JsonResponse({"results": 'success'})
    except Exception as e:
        print(e)
        return JsonResponse({'statusMsg': 'error'}, status=404)



"""if __name__ == "__main__":
    run_google_scraper()"""