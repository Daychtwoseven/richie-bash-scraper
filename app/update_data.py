import re
import time
from datetime import datetime

from app.models import Business
from app.utils import custom_windows_user_agent, is_website, check_similarity, capsolver_api, facebook
from urllib.parse import urlencode, urlparse
from curl_cffi import requests as cfffi
from bs4 import BeautifulSoup
import json


class UpdateData:
    def __init__(self):
        self.session = cfffi.Session()
        self.site_key = '6LdhIq8UAAAAAO3N-yHHx5_vmutjCSQW47P4jLH1'
        self.run_scraper()

    def run_scraper(self):
        today = datetime.now()
        for row in Business.objects.exclude(last_update__date=today):
            name = row.name
            address = row.address
            business_domain = urlparse(row.website).netloc if row.website else None
            yelp_data = self.yelp(name, address, business_domain)
            facebook_data = self.facebook(name, row.type.address)

            if yelp_data:
                print(f"Scraping Yelp Desc: {row.name} | Location: {row.address} | Status: Found")
                row.yelp_url = yelp_data['yelp_url']
                row.yelp_reviews_count = yelp_data['review_count']
                row.yelp_rating = yelp_data['rating']

            if facebook_data:
                print(f"Scraping FB Desc: {row.name} | Location: {row.address} | Status: Found")
                print(facebook_data)
                row.facebook_url = facebook_data['url']
                row.facebook_rating = facebook_data['rating']
                row.facebook_reviews_count = facebook_data['review_count']

            row.last_update = today
            row.save()
            time.sleep(15)


    def yelp(self, name, address, business_domain):
        data = None
        try:
            find_desc = urlencode({'find_desc': name})
            find_loc = urlencode({'find_loc': address})

            # Define the headers
            headers = {
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                'accept-language': 'en-US,en;q=0.5',
                'cache-control': 'max-age=0',
                'priority': 'u=0, i',
                'sec-ch-ua': '"Chromium";v="130", "Brave";v="130", "Not?A_Brand";v="99"',
                'sec-ch-ua-arch': '"x86"',
                'sec-ch-ua-full-version-list': '"Chromium";v="130.0.0.0", "Brave";v="130.0.0.0", "Not?A_Brand";v="99.0.0.0"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-model': '""',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'document',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-site': 'same-origin',
                'sec-fetch-user': '?1',
                'sec-gpc': '1',
                'upgrade-insecure-requests': '1',
                'user-agent': custom_windows_user_agent(),
                'cookie': 'datadome=07onDczXO4LfzeO5EiTdnoPTGdOc3XDUcOCZ9Oevt02ojkGpo0x8Co2ngN5TyLIaw5hvtvfii9k6hOoQR6rVHQzK8gnyG3IGGBhrmYUZVoUMLLncH5V7Mu~CENvifYGC'
            }

            response = self.session.get(f"https://www.yelp.com/search?{find_desc}&{find_loc}", headers=headers)
            # headers['cookie'] = f'datadome={response.cookies.get('datadome')}'
            # response = session.get(f"https://www.yelp.com/search?{find_desc}&{find_loc}", headers=headers)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                script_tag = soup.find('script', type='application/json', attrs={
                    'data-hypernova-key': 'yelpfrontend__831__yelpfrontend__GondolaSearch__dynamic'
                })

                if script_tag:
                    script_content = script_tag.string
                    temp_data = json.loads(script_content[4:-3])
                    business = temp_data['legacyProps']['searchAppProps']['searchPageProps'][
                        'mainContentComponentsListProps']

                    for row in business:
                        if 'searchResultBusiness' in row:
                            yelp_name = row['searchResultBusiness']['name']
                            rating = row['searchResultBusiness']['rating']
                            review_count = row['searchResultBusiness']['reviewCount']
                            yelp_address = row['searchResultBusiness']['formattedAddress']
                            website = row['searchResultBusiness']['website']['href'] if row['searchResultBusiness'][
                                'website'] else None
                            yelp_url = f"https://www.yelp.com{row['searchResultBusiness']['businessSectionUrls']['reviews']}"

                            if is_website(website) and business_domain:
                                website_domain = urlparse(website).netloc
                                if website_domain == business_domain:
                                    data = {
                                        'name': yelp_name,
                                        'rating': rating,
                                        'review_count': review_count,
                                        'address': yelp_address,
                                        'website': website,
                                        'yelp_url': yelp_url
                                    }
                                    break

                            if check_similarity(name.split('-')[0].lower(), yelp_name.split('-')[0].lower() or check_similarity(
                                    address.split(',')[0].lower(), yelp_address.split(',')[0].lower())):
                                data = {
                                    'name': yelp_name,
                                    'rating': rating,
                                    'review_count': review_count,
                                    'address': yelp_address,
                                    'website': website,
                                    'yelp_url': yelp_url
                                }
                                break

                else:
                    print("Script tag not found.")
            else:
                print(f"Request failed with status code: {response.status_code}")
            return data

        except Exception as e:
            print(f"Error from yelp: {e}")
            return data


    def facebook(self, name, address):
        data = None
        try:
            query = urlencode({'q': f"{name} in {address} facebook page"})
            location = urlencode({'location': address})
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
                temp_data = response.json()
                if 'organic_results' in temp_data and len(temp_data['organic_results']) > 0:
                    temp_data = temp_data['organic_results'][0]
                    title = temp_data['title']
                    if check_similarity(re.split(r'[-|]', name)[0].lower(), re.split(r'[-|]', title)[0].lower()) and 'rich_snippet' in temp_data and 'top' in temp_data['rich_snippet'] and 'detected_extensions' in temp_data['rich_snippet']['top']:
                        data = {
                            'name': temp_data['title'],
                            'rating': temp_data['rich_snippet']['top']['detected_extensions']['rating'] if 'rating' in temp_data['rich_snippet']['top']['detected_extensions'] else '',
                            'review_count': temp_data['rich_snippet']['top']['detected_extensions']['reviews'] if 'reviews' in temp_data['rich_snippet']['top']['detected_extensions'] else '',
                            'url': temp_data['link'],
                        }
                        return data
            return data

        except Exception as e:
            print(e)
            return data