import time
from urllib.parse import urlparse, parse_qs
from bs4 import BeautifulSoup
import requests

session = requests.Session()

for i in range(0, 20):
    url = "https://www.google.com/search?q=NJ+State+Auto+Used+Cars+Jersey+City+in+Jersey+City%2C+NJ+facebook.com+and+yelp.com"

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
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36'
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    print(response.text)

    response = session.request("GET", url, headers=headers, data=payload)

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

            print(f"Title: {title} | Rating: {rating} | Reviews: {reviews} | Link: {link}")

        time.sleep(15)