import re
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

from app.models import Business, BusinessReviews
from app.utils import custom_windows_user_agent, is_website, check_similarity, capsolver_api
from urllib.parse import urlencode, urlparse
from curl_cffi import requests
from bs4 import BeautifulSoup
import json
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')
django.setup()


class UpdateData:
    def __init__(self):
        self.session = requests.Session()
        self.site_key = '6LdhIq8UAAAAAO3N-yHHx5_vmutjCSQW47P4jLH1'
        self.run_scraper()

    def run_scraper(self):
        today = datetime.now()
        business = Business.objects.exclude(last_update__date=today)
        print('here')
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
        # for row in Business.objects.exclude(last_update__date=today):
        name = row.name
        address = row.address
        business_domain = urlparse(row.website).netloc if row.website else None
        updated_data = self.update_scraper(name, address, row.type.address,
                                           row.google_pid if row.google_pid else None, row)
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
            # google_business_review = BusinessReviews.objects.create(business=row, content=updated_data['google_review_data'])

        #time.sleep(30)

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
            temp_json_data = response.json()
            if 'organic_results' not in temp_json_data and 'search_metadata' in temp_json_data and 'json_endpoint' in temp_json_data['search_metadata']:
                time.sleep(2)
                response = self.session.request("GET", response.json()['search_metadata']['json_endpoint'])

            if response.status_code == 200:
                temp_json_data = response.json()
                if 'organic_results' in temp_json_data and len(temp_json_data['organic_results']) > 0:

                    for row in temp_json_data['organic_results']:
                        temp_data = row
                        title = temp_data['title']
                        current_domain = urlparse(temp_data['link']).netloc
                        if current_domain == 'www.facebook.com' and data['facebook_result'] == 0 and check_similarity(
                                re.split(r'[-|]', name)[0].lower(),
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
                        if current_domain == 'www.yelp.com' and data['yelp_result'] == 0 and check_similarity(
                                re.split(r'[-|]', name)[0].lower(),
                                re.split(r'[-|]', title)[
                                    0].lower()) and 'rich_snippet' in temp_data and 'top' in \
                                temp_data['rich_snippet'] and 'detected_extensions' in temp_data['rich_snippet'][
                            'top'] and 'source' in temp_data and 'yelp' in temp_data['source'].lower():
                            data['yelp_rating'] = temp_data['rich_snippet']['top']['detected_extensions'][
                                'rating'] if 'rating' in temp_data['rich_snippet']['top']['detected_extensions'] else ''
                            data['yelp_review'] = temp_data['rich_snippet']['top']['detected_extensions'][
                                'reviews'] if 'reviews' in temp_data['rich_snippet']['top'][
                                'detected_extensions'] else ''
                            data['yelp_url'] = temp_data['link']
                            data['yelp_result'] = 1

                        if 'source' in temp_data and data['website_result'] == 0 and check_similarity(
                                re.split(r'[-|]', name)[0].lower(),
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
                    if 'local_result' in temp_json_data:
                        data['google_rating'] = temp_json_data['rating'] if 'rating' in temp_json_data[
                            'local_result'] else ''
                        data['google_review'] = temp_json_data['reviews'] if 'reviews' in temp_json_data[
                            'local_result'] else ''

            return data

        except Exception as e:
            print(e)
            return data

    def update_scraper_v2(self, name, address, location, google_pid, business):
        try:
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
            query = urlencode({'q': f"{name} in {address} facebook.com and yelp.com"})
            url = f"https://www.google.com/search?q={query}"

            payload = {}
            headers = {
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                'accept-language': 'en-US,en;q=0.7',
                'cache-control': 'no-cache',
                'cookie': 'AEC=AVYB7crnQFZRnAANjtV0JgCSG2PV2X8rMN1R59ExQ8ozLIuYPsB8u5CuJw; NID=518=AIvyY-pAiJJzHQtgu8s64HLW2zFiW9Ov7AQ-Ei9Cpv-dLX_CF0UjiWIOJnVst0h4EYPCi0U7LUqCH7r1ihuzU7vFEz5_w_FBw77aPaguP5axosFHi7_58gfUyKvTNyCrh-FOFfGpHGbQOyu_NGLPqQkeWm2JZK8fEIp5wu9nKyznfTFpHYJeHipk5lsmtpe4sLI',
                'pragma': 'no-cache',
                'priority': 'u=0, i',
                'referer': 'https://www.google.com/',
                'sec-ch-ua': '"Chromium";v="130", "Brave";v="130", "Not?A_Brand";v="99"',
                'sec-ch-ua-arch': '"x86"',
                'sec-ch-ua-bitness': '"64"',
                'sec-ch-ua-full-version-list': '"Chromium";v="130.0.0.0", "Brave";v="130.0.0.0", "Not?A_Brand";v="99.0.0.0"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-model': '""',
                'sec-ch-ua-platform': '"Windows"',
                'sec-ch-ua-platform-version': '"15.0.0"',
                'sec-ch-ua-wow64': '?0',
                'sec-fetch-dest': 'document',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-site': 'same-origin',
                'sec-fetch-user': '?1',
                'sec-gpc': '1',
                'upgrade-insecure-requests': '1',
                'user-agent': custom_windows_user_agent()
            }

            response = self.session.request("GET", url, headers=headers, data=payload)
            if response.status_code != 200:
                for i in range(1, 5):
                    print(f"Waiting 100seconds...")
                    time.sleep(int(str(f"{i}00")))
                    response = self.session.request("GET", url, headers=headers, data=payload)
                    if response.status_code == 200:
                        break

            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                results_div = soup.find('div', class_="dURPMd")
                results = results_div.findAll('div', class_='N54PNb')
                for row in results:
                    # Find the <a> element once
                    link_element = row.find('a', {'jsname': 'UWckNb'})
                    link = link_element['href'] if link_element else ''

                    # Find the <h3> element once
                    title_element = row.find('h3', class_='LC20lb')
                    title = title_element.text if title_element else ''

                    # Find the rating element once
                    rating_element = row.find('span', class_='yi40Hd')
                    rating = rating_element.text if rating_element else ''

                    # Find the reviews element once
                    reviews_element = row.find('span', class_='RDApEe')
                    reviews = reviews_element.text.replace('(', '').replace(')', '') if reviews_element else ''

                    current_domain = urlparse(link).netloc
                    if current_domain == 'www.facebook.com' and data['facebook_result'] == 0 and check_similarity(
                            re.split(r'[-|]', name)[0].lower(),re.split(r'[-|]', title)[0].lower()):
                        data['facebook_rating'] = rating if rating != '' else print(' ')
                        data['facebook_review'] = reviews if reviews != '' else print(' ')
                        data['facebook_url'] = link if link != '' else print(' ')
                        data['facebook_result'] = 1

                    if current_domain == 'www.yelp.com' and data['yelp_result'] == 0 and check_similarity(
                            re.split(r'[-|]', name)[0].lower(),re.split(r'[-|]', title)[0].lower()):
                        data['yelp_rating'] = rating if rating != '' else print(' ')
                        data['yelp_review'] = reviews if reviews != '' else print(' ')
                        data['yelp_url'] = link if link != '' else print(' ')
                        data['yelp_result'] = 1

                    if current_domain != 'www.yelp.com' and current_domain != 'www.facebook.com' and data['website_result'] == 0 and check_similarity(
                            re.split(r'[-|]', name)[0].lower(),re.split(r'[-|]', title)[0].lower()):

                        data['website_url'] = link if link != '' else print(' ')
                        data['website_result'] = 1

            print(f"Updating {name} | {address} | Status: {response.status_code}")
            return data

        except Exception as e:
            print(e)
            return data
"""UpdateData()
"""