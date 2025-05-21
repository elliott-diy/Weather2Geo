import csv
import os
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

locations = []

start = time.time()

# Step 1: Load Locations
with open("CA.csv", 'r', encoding='utf-8') as file:
    reader = csv.reader(file, delimiter='\t')
    for i, row in enumerate(reader):
        if i == 0 and any(cell.lower() in ['name', 'city', 'state'] for cell in row):
            continue
        if len(row) < 3:
            continue
        location = row[2].strip() if len(row) > 2 else 'Unknown'
        latitude = row[-3].strip()
        longitude = row[-2].strip()
        if latitude and longitude:
            locations.append({
                'location': location,
                'latitude': latitude,
                'longitude': longitude,
                'temp': None,
                'cap': None,
                'status': None
                'timezone': None,
            })

print(f"Loaded {len(locations)} locations.")

# Step 2: Weather Fetching Function
def fetch_weather(location):
    if not location['location'] or not location['latitude'] or not location['longitude']:
        location['status'] = 'Invalid location data'
        return location

    url = f"https://api.msn.com/weather/overview?apikey=UhJ4G66OjyLbn9mXARgajXLiLw6V75sHnfpU60aJBB&lat={location['latitude']}&lon={location['longitude']}&units=C"

    try:
        r = requests.get(url, timeout=5)
        location['status_code'] = r.status_code

        if r.status_code == 200:
            data = r.json()
            current = data['value'][0]['responses'][0]['weather'][0]['current']
            location['temp'] = current.get('temp')
            location['cap'] = current.get('cap')
            location['timezone'] = data['value'][0]['responses'][0]['weather'][0]['timezone']
            location['status'] = 'Success'
        else:
            location['status'] = f"HTTP {r.status_code}"

    except Exception as e:
        location['status'] = f"Error: {e}"

    return location

with ThreadPoolExecutor(max_workers=50) as executor:
    futures = [executor.submit(fetch_weather, loc) for loc in locations]
    for future in as_completed(futures):
        result = future.result()
        print(f"{result['location']}: Temp {result['temp']}°C, State {result['cap']} ({result['status']})")

matching_locations = [
    loc for loc in locations
    if loc['temp'] is not None and loc['cap'] == "Mostly cloudy" and loc['temp'] == 14.0
]
print("")
print("")
print(f"\nFound {len(matching_locations)} matching locations with 13.0°C and Light rain:")
for loc in matching_locations:
    print(f"{loc['location']}: {loc['temp']}°C and {loc['cap']}")

stop = time.time()
print(f"\nTotal time taken: {stop - start:.2f} seconds")
