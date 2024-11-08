import os
import sys
import django
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import time
import re
import json
from urllib.parse import urlencode, urlparse
from curl_cffi import requests
from bs4 import BeautifulSoup

# Set the current path and add to sys.path
current_path = Path(__file__).resolve().parent
sys.path.append(str(current_path))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')
django.setup()

# Django model imports
from app.models import Business, BusinessReviews
from app.utils import custom_windows_user_agent, is_website, check_similarity, capsolver_api


class UpdateData:
    def __init__(self):
        self.session = requests.Session()
        self.site_key = '6LdhIq8UAAAAAO3N-yHHx5_vmutjCSQW47P4jLH1'
        self.run_scraper()

    def run_scraper(self):
        today = datetime.now()
        # Exclude businesses already updated today
        business = Business.objects.exclude(last_update__date=today)

        with ThreadPoolExecutor(max_workers=1000) as executor:
            # Submit tasks to the executor
            futures = {executor.submit(self.run_scraper_s1, row): row for row in business}

            # Collect results as they complete
            for future in futures:
                try:
                    result = future.result()  # This will block until the result is available
                except Exception as e:
                    print(f"Error processing item {futures[future]}: {str(e)}")

    def run_scraper_s1(self, row):
        today = datetime.now()
        name = row.name
        address = row.address
        business_domain = urlparse(row.website).netloc if row.website else None

        updated_data = self.update_scraper(name, address, row.type.address,
                                           row.google_pid if row.google_pid else None, row)

        if updated_data:
            # Update the fields with the new data
            row.facebook_rating = updated_data['facebook_rating']
            row.facebook_reviews_count = updated_data['facebook_review']
            row.facebook_url = updated_data['facebook_url']
            row.yelp_rating = updated_data['yelp_rating']
            row.yelp_reviews_count = updated_data['yelp_review']
            row.yelp_url = updated_data['yelp_url']
            row.google_rating = updated_data['google_rating']
            row.google_reviews_count = updated_data['google_review']
            row.last_update = today
            row.website = updated_data['website_url']
            row.save()

    def update_scraper(self, name, address, location, google_pid, business):
        data = {
            'facebook_rating': business.facebook_rating,
            'facebook_review': business.facebook_reviews_count,
            'facebook_url': business.facebook_url,
            'facebook_result': 0,
            'yelp_rating': business.yelp_rating,
            'yelp_review': business.yelp_reviews_count,
            'yelp_url': business.yelp_url,
            'yelp_result': 0,
            'google_rating': business.google_rating,
            'google_review': business.google_reviews_count,
            'google_review_data': {},
            'website_result': 0,
            'website_url': ''
        }

        try:
            query = urlencode({'q': f"{name} in {address} facebook.com and yelp.com"})
            location = urlencode({'location': location})
            g_captcha = capsolver_api("https://serpapi.com/", self.site_key)
            url = f"https://serpapi.com/search.json?engine=google&q={query}&{location}&google_domain=google.com&gl=us&hl=en&async=true&gRecaptchaResponse={g_captcha}"

            headers = {
                'accept': 'application/json, text/javascript, */*; q=0.01',
                'accept-language': 'en-US,en;q=0.7',
                'cookie': '',
                'sec-ch-ua': '"Chromium";v="130", "Brave";v="130", "Not?A_Brand";v="99"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-origin',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36'
            }

            response = self.session.request("GET", url, headers=headers)
            temp_json_data = response.json()

            if 'organic_results' not in temp_json_data and 'search_metadata' in temp_json_data and 'json_endpoint' in \
                    temp_json_data['search_metadata']:
                time.sleep(2)
                response = self.session.request("GET", response.json()['search_metadata']['json_endpoint'])

            if response.status_code == 200:
                temp_json_data = response.json()
                if 'organic_results' in temp_json_data and len(temp_json_data['organic_results']) > 0:
                    for row in temp_json_data['organic_results']:
                        title = row.get('title', '')
                        current_domain = urlparse(row['link']).netloc

                        # Process Facebook, Yelp, and Website results
                        if current_domain == 'www.facebook.com' and data['facebook_result'] == 0 and check_similarity(
                                re.split(r'[-|]', name)[0].lower(), re.split(r'[-|]', title)[0].lower()):
                            data['facebook_rating'] = row.get('rating', '')
                            data['facebook_review'] = row.get('reviews', '')
                            data['facebook_url'] = row['link']
                            data['facebook_result'] = 1

                        if current_domain == 'www.yelp.com' and data['yelp_result'] == 0 and check_similarity(
                                re.split(r'[-|]', name)[0].lower(), re.split(r'[-|]', title)[0].lower()):
                            data['yelp_rating'] = row.get('rating', '')
                            data['yelp_review'] = row.get('reviews', '')
                            data['yelp_url'] = row['link']
                            data['yelp_result'] = 1

                        if current_domain != 'www.yelp.com' and current_domain != 'www.facebook.com' and data[
                            'website_result'] == 0 and check_similarity(re.split(r'[-|]', name)[0].lower(),
                                                                        re.split(r'[-|]', title)[0].lower()):
                            data['website_url'] = row['link']
                            data['website_result'] = 1

            # If we have a Google PID, process additional information
            if google_pid:
                g_captcha = capsolver_api("https://serpapi.com/", self.site_key)
                url = f"https://serpapi.com/search.json?engine=google_local&q={query}&google_domain=google.com&async=true&gRecaptchaResponse={g_captcha}&ludocid={google_pid}"
                response = self.session.request("GET", url, headers=headers)
                time.sleep(2)
                response = self.session.request("GET", response.json()['search_metadata']['json_endpoint'])
                if response.status_code == 200:
                    temp_json_data = response.json()
                    if 'local_result' in temp_json_data:
                        data['google_rating'] = temp_json_data['local_result'].get('rating', '')
                        data['google_review'] = temp_json_data['local_result'].get('reviews', '')

            return data

        except Exception as e:
            print(f"Error in update_scraper: {e}")
            return data


# Initialize the scraper class
UpdateData()
