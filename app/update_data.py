import re
import time
from datetime import datetime

from app.models import Business, BusinessReviews
from app.utils import custom_windows_user_agent, is_website, check_similarity, capsolver_api
from urllib.parse import urlencode, urlparse
from curl_cffi import requests
from bs4 import BeautifulSoup
import json


class UpdateData:
    def __init__(self):
        self.session = requests.Session()
        self.site_key = '6LdhIq8UAAAAAO3N-yHHx5_vmutjCSQW47P4jLH1'
        self.run_scraper()

    def run_scraper(self):
        today = datetime.now()
        #for row in Business.objects.exclude(last_update__date=today):
        for row in Business.objects.all():
            name = row.name
            address = row.address
            business_domain = urlparse(row.website).netloc if row.website else None
            updated_data = self.update_scraper(name, address, row.type.address, row.google_pid if row.google_pid else None, row)

            if updated_data:
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
                #google_business_review = BusinessReviews.objects.create(business=row, content=updated_data['google_review_data'])

            print(f"Updating {name} | {address}")

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
                'priority': 'u=1, i',
                'referer': '',
                'sec-ch-ua': '"Chromium";v="130", "Brave";v="130", "Not?A_Brand";v="99"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-origin',
                'sec-gpc': '1',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
                'x-csrf-token': '',
                'x-requested-with': 'XMLHttpRequest'
            }

            response = self.session.request("GET", url, headers=headers)
            time.sleep(2)
            response = self.session.request("GET", response.json()['search_metadata']['json_endpoint'])

            if response.status_code == 200:
                temp_json_data = response.json()
                if 'organic_results' in temp_json_data and len(temp_json_data['organic_results']) > 0:

                    for row in temp_json_data['organic_results']:
                        temp_data = row
                        title = temp_data['title']
                        current_domain = urlparse(temp_data['link']).netloc
                        if current_domain == 'www.facebook.com' and data['facebook_result'] == 0 and check_similarity(re.split(r'[-|]', name)[0].lower(),
                                                                     re.split(r'[-|]', title)[
                                                                         0].lower()) and 'rich_snippet' in temp_data and 'top' in \
                                temp_data['rich_snippet'] and 'detected_extensions' in temp_data['rich_snippet'][
                            'top'] and 'source' in temp_data and 'facebook' in temp_data['source'].lower():
                            data['facebook_rating'] = temp_data['rich_snippet']['top']['detected_extensions'][
                                'rating'] if 'rating' in temp_data['rich_snippet']['top']['detected_extensions'] else ''
                            data['facebook_review'] = temp_data['rich_snippet']['top']['detected_extensions'][
                                'reviews'] if 'reviews' in temp_data['rich_snippet']['top'][
                                'detected_extensions'] else ''
                            data['facebook_url'] = temp_data['link']
                            data['facebook_result'] = 1
                        if current_domain == 'www.yelp.com' and data['yelp_result'] == 0 and check_similarity(re.split(r'[-|]', name)[0].lower(),
                                                                 re.split(r'[-|]', title)[
                                                                     0].lower()) and 'rich_snippet' in temp_data and 'top' in \
                                temp_data['rich_snippet'] and 'detected_extensions' in temp_data['rich_snippet'][
                            'top'] and 'source' in temp_data and 'yelp' in temp_data['source'].lower():
                            data['yelp_rating'] = temp_data['rich_snippet']['top']['detected_extensions'][
                                'rating'] if 'rating' in temp_data['rich_snippet']['top']['detected_extensions'] else ''
                            data['yelp_review'] = temp_data['rich_snippet']['top']['detected_extensions'][
                                'reviews'] if 'reviews' in temp_data['rich_snippet']['top'][
                                'detected_extensions'] else ''
                            data['urlp_url'] = temp_data['link']
                            data['yelp_result'] = 1

                        if 'source' in temp_data and data['website_result'] == 0 and check_similarity(re.split(r'[-|]', name)[0].lower(),
                                                                 re.split(r'[-|]', temp_data['source'])[
                                                                     0].lower()):
                            data['website_url'] = temp_data['link'] if 'link' in temp_data else ''
                            data['website_result'] = 1


            if google_pid:
                g_captcha = capsolver_api("https://serpapi.com/", self.site_key)
                url = f"https://serpapi.com/search.json?engine=google_local&{query}&google_domain=google.com&async=true&gRecaptchaResponse={g_captcha}&ludocid={google_pid}"
                response = self.session.request("GET", url, headers=headers)
                time.sleep(2)
                response = self.session.request("GET", response.json()['search_metadata']['json_endpoint'])
                if response.status_code == 200:
                    temp_json_data = response.json()
                    data['google_rating'] = temp_json_data['rating'] if 'rating' in temp_json_data else ''
                    data['google_review'] = temp_json_data['reviews'] if 'reviews' in temp_json_data else ''

            return data

        except Exception as e:
            print(e)
            return data