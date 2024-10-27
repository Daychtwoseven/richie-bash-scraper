from python3_capsolver.recaptcha import ReCaptcha
from urllib.parse import urlencode
import requests
import json
import time


def serpapi(q, location):
    data = []
    try:
        pages = [0, 20, 40, 60, 80, 100, 120, 140, 160, 180, 200]
        site_key = '6LdhIq8UAAAAAO3N-yHHx5_vmutjCSQW47P4jLH1'
        query = urlencode({'q': f"{q} in {location}"})
        for i in range(0, 100):
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

