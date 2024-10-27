import time
from geopy.geocoders import Nominatim

# Create a geolocator object with a unique user agent
geolocator = Nominatim(user_agent="geoapiExercises")

# List of cities with full state and country
locations = [
    "Abilene, Texas, United States",
    "New York, New York, United States",
    "Los Angeles, California, United States",
    "Chicago, Illinois, United States",
    "Houston, Texas, United States"
]

for location in locations:
    try:
        loc = geolocator.geocode(location)
        if loc:
            print(f"{location}: Latitude: {loc.latitude}, Longitude: {loc.longitude}")
        else:
            print(f"{location}: Location not found.")
    except Exception as e:
        print(f"Error retrieving {location}: {e}")
    time.sleep(1)  # Sleep to avoid hitting rate limits
