import random
import re
from fuzzywuzzy import fuzz
from fake_useragent import UserAgent
from user_agent import generate_user_agent
import validators
from python3_capsolver.recaptcha import ReCaptcha
from urllib.parse import urlencode, urlparse, parse_qs
from bs4 import BeautifulSoup
import requests
import json
import time


def serpapi(q, location):
    data = []
    try:
        pages = [0, 20, 40, 60, 80, 100, 120, 140, 160, 180, 200]
        site_key = '6LdhIq8UAAAAAO3N-yHHx5_vmutjCSQW47P4jLH1'
        query = urlencode({'q': f"{q} in {location}"})
        for i in range(0, 10):
            print(f"Running {q} {location} | Page: {pages[i]}")
            g_captcha = capsolver_api("https://serpapi.com/", site_key)
            url = f"https://serpapi.com/search.json?engine=google_maps&q={query}&google_domain=google.com&hl=en&type=search&async=true&gRecaptchaResponse={g_captcha}&start={pages[i]}&ll=%4040.7455096%2C-74.0083012%2C14z"
            payload = {}
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
            response = requests.request("GET", url, headers=headers, data=payload, proxies={
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


def yelp(q, loc, business_domain):
    from curl_cffi import requests as cfffi
    data = None
    session = cfffi.Session()
    try:
        find_desc = urlencode({'find_desc': q})
        find_loc = urlencode({'find_loc': loc})

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

        response = session.get(f"https://www.yelp.com/search?{find_desc}&{find_loc}", headers=headers)
        #headers['cookie'] = f'datadome={response.cookies.get('datadome')}'
        #response = session.get(f"https://www.yelp.com/search?{find_desc}&{find_loc}", headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            script_tag = soup.find('script', type='application/json', attrs={
                'data-hypernova-key': 'yelpfrontend__831__yelpfrontend__GondolaSearch__dynamic'
            })

            if script_tag:
                script_content = script_tag.string
                temp_data = json.loads(script_content[4:-3])
                business = temp_data['legacyProps']['searchAppProps']['searchPageProps']['mainContentComponentsListProps']

                for row in business:
                    if 'searchResultBusiness' in row:
                        name = row['searchResultBusiness']['name']
                        rating = row['searchResultBusiness']['rating']
                        review_count = row['searchResultBusiness']['reviewCount']
                        address = row['searchResultBusiness']['formattedAddress']
                        website = row['searchResultBusiness']['website']['href'] if row['searchResultBusiness']['website'] else None
                        yelp_url = f"https://www.yelp.com{row['searchResultBusiness']['businessSectionUrls']['reviews']}"

                        if is_website(website) and business_domain:
                            website_domain = urlparse(website).netloc
                            if website_domain == business_domain:
                                data = {
                                    'name': name,
                                    'rating': rating,
                                    'review_count': review_count,
                                    'address': address,
                                    'website': website,
                                    'yelp_url': yelp_url
                                }
                                break

                        if check_similarity(q.split('-')[0].lower(), name.split('-')[0].lower() or check_similarity(loc.split(',')[0].lower(), address.split(',')[0].lower())):
                            data = {
                                'name': name,
                                'rating': rating,
                                'review_count': review_count,
                                'address': address,
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
        print(f"An error occurred: {e}")
        return data


def facebook(q, loc):
    try:
        import requests

        url = "https://serpapi.com/search.json?engine=google&q=2nt+Chszxcce+Mqotors+3945+S+1st+St%2C+Abxzc2ilene%2C+TX+7931605++facebook+page&location=Austin%2C+Texas%2C+United+States&google_domain=google.com&gl=us&hl=en&async=true&gRecaptchaResponse=03AFcWeA49HiwGrww9hA05918jJKJNR7hldQeTjJryjQb862vgd3LClxXbftYbrQBbLvLIYcNKX6QB93jUCFiVU8VqBTBR29WL4nUpNcp1ucWGpnF_LS_VjSvJ4U8CClt7jhnNl_7NzHlUu2yQDS7WGDTPHlBLJgU_uLKwr4omEWBEfmBZwPzs6uxr4cziS-a1gMrQM6ZRooVr8EUJLCwxtdLMkPv_yjcSxBzskYrUUDXTCYvYnNYnbqKaM5jcrktL80Fy9DXC3AsS7awjHEs2xOIuQg4veMe03AvlocoTcUudwuFsnOWYJo0PATViHGJuBoHRzR6Zwx9tcne0EO1NWHnXU_sdxv_QKimcDFyMrtPPeA2cNbkOub-aqHnj-GHeimSUeOtLJZedl8OJWJJZU_hhli5b-jpEcwGwrZ6a4f6satt7glzOk7yqUB4-5C7zM5ndXeSEO6PziSpqZcUOO7eaECK8Rv-Yf4ijag_enQtgv5Cum6dhg74Vyaig8lvUBVe6zYKDvEefKZuk9b5PEUILFxINlyCQ-r5PUProw9KrA3ZnD2Y62kl8Qqb2X0wdpoAa8EumKayx6YSlKERl8NDAX9TgtnPRQKm2PtYRijSOc5TuW5vNN3x3VQwE8xatmF5TknOybhup_hLv7pIbSA4h7ed23GVVIOFjDZX4cN9TcbrgaUPxZ9EVVf-5BZrL9pSIOQLwg-6NcFbMTQ4GN2WYpu77fFwVdNbP4qdICZcDBtJVUTew-kR1ZcLdr-7jwjIfQNW0FPNQmWkFG5Twq7sYPa0kBxkwFJ9VhXdOjb417aaLwoIoc0mu4AHgvV_ixId7-Vp3I-5gtxc6fMSb4z5tF0S0yht8IXFZ9_hmnSgMaWTo1p37Jluu_PT7IQSr_mBTyq1aoi7H-SuRHkJ_Ly6N2JU5p7sxn9O-8ugu0ZlfOM8cRH_5154"

        payload = {}
        headers = {
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'accept-language': 'en-US,en;q=0.7',
            'cookie': 'intercom-id-yzck75jr=b3266f4b-1c01-4191-8049-4d38166e1967; intercom-session-yzck75jr=; intercom-device-id-yzck75jr=8463d8d6-3e44-4072-a64a-0510ae811042',
            'priority': 'u=1, i',
            'referer': 'https://serpapi.com/playground?q=2nt+Chszxcce+Mqotors+3945+S+1st+St%2C+Abxzc2ilene%2C+TX+7931605++facebook+page&location=Austin%2C+Texas%2C+United+States&gl=us&hl=en',
            'sec-ch-ua': '"Chromium";v="130", "Brave";v="130", "Not?A_Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'sec-gpc': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
            'x-csrf-token': 'QsU4KTKQ11YjCrjvU54Y5lSkj3oz3pCRbQ5Ons/GerA6U/G1CHouhdTDlDoD1VOZootPEN4Cuko8rvndqD7O1A==',
            'x-requested-with': 'XMLHttpRequest'
        }

        response = requests.request("GET", url, headers=headers, data=payload)

        print(response.text)

    except Exception as e:
        print(e)


def serpapi_reviews(place_id):
    try:
        site_key = '6LdhIq8UAAAAAO3N-yHHx5_vmutjCSQW47P4jLH1'
        g_captcha = capsolver_api("https://serpapi.com/", site_key)
        url = f"https://serpapi.com/search.json?engine=google_maps_reviews&place_id={place_id}&hl=en&async=true&gRecaptchaResponse={g_captcha}"
        payload = {}
        headers = {
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'accept-language': 'en-US,en;q=0.7',
            'priority': 'u=1, i',
            'cookie': '',
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

        response = requests.request("GET", url, headers=headers, data=payload)
        print(response.json())
    except Exception as e:
        print(e)
        return None


def capsolver_api(url, site_key, max_retries=3, retry_delay=5):
    retry_count = 0

    while retry_count < max_retries:
        try:

            start_time = time.time()
            result = ReCaptcha(
                api_key='CAP-D4FC4D3226B5C2A9BC366DA9DE49205A',
                captcha_type="ReCaptchaV2TaskProxyLess",
                websiteURL=url,
                websiteKey=site_key
            ).captcha_handler()

            data = json.loads(result.json())
            captcha_code = data['solution']['gRecaptchaResponse']

            end_time = time.time()  # Capture end time
            duration = end_time - start_time
            minutes, seconds = divmod(duration, 60)
            print(f"capsolver running time: {int(minutes)}:{int(seconds):02d}")

            return captcha_code
        except Exception as e:
            retry_count += 1
            print(f"Attempt {retry_count} failed: {e}")
            if retry_count >= max_retries:
                print("Max retries reached. Unable to get CAPTCHA.")
                return None
            time.sleep(retry_delay)


def get_yelp_redirected_url(url):
    try:
        check = requests.get(url)
        # Step 1: Decode the bytes to a string
        html_content = check.content.decode('utf-8')

        # Step 2: Create a BeautifulSoup object
        soup = BeautifulSoup(html_content, 'html.parser')

        # Step 3: Find all script tags
        script_tags = soup.find_all('script')

        # Step 4: Extract the location.replace URL from the script content
        for script in script_tags:
            if 'location.replace' in script.text:
                # Use regex to extract the URL
                match = re.search(r'location\.replace\("([^"]+)"\)', script.text)
                if match:
                    redirect_url = match.group(1)
                    parsed_url = urlparse(redirect_url.replace('\\u0026', '&'))

                    # Step 2: Extract query parameters
                    query_params = parse_qs(parsed_url.query)
                    url_value = query_params.get('url', [None])[0]
                    return urlparse(url_value).netloc
        return None
    except Exception as e:
        print(e)
        return None


def is_website(url):
    try:
        return validators.url(url)
    except Exception as e:
        print(e)


def check_similarity(fname, sname):
    try:
        similarity = fuzz.ratio(fname, sname)

        # Check if they are similar enough
        if similarity > 80:  # Adjust the threshold as needed
            return True

        else:
            return False
    except Exception as e:
        print(e)
        return False


def custom_windows_user_agent():
    browsers = [
        "Chrome/91.0.4472.124",
        "Firefox/89.0",
        "Edg/93.0.961.38",
        "Safari/537.36"
    ]
    browser = random.choice(browsers)
    return f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) {browser} AppleWebKit/537.36 (KHTML, like Gecko)"
