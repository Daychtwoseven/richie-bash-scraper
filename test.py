from urllib.parse import urlparse, parse_qs

from bs4 import BeautifulSoup
import requests
import re


check = requests.get("https://www.yelp.com/adredir?ad_business_id=d0VNyBz91TX3ZchNAGJMog&amp;campaign_id=NRyb9YEZS9Er3H6ExDjORQ&amp;click_origin=search_results_visit_website&amp;placement=vertical_1&amp;placement_slot=2&amp;redirect_url=https%3A%2F%2Fwww.yelp.com%2Fbiz_redir%3Fcachebuster%3D1730174505%26s%3D406d2df9760d4a2cc3635976844d46d3fa1b94fc6af580cf6202bf17abb4b3f4%26src_bizid%3Dd0VNyBz91TX3ZchNAGJMog%26url%3Dhttp%253A%252F%252Fbuysideauto.com%26website_link_type%3Dwebsite&amp;request_id=9c20dfa7a95e11f1&amp;signature=a0d425c2933e19f16eddb54f917e7ba0f3b495a92a164369448326e670853221&amp;slot=3")
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

