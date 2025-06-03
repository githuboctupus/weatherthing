import csv
import os
from glob import glob
from datetime import datetime
from geopy.geocoders import Nominatim
from geopy.distance import geodesic

def haversine_within_radius(lat1, lon1, lat2, lon2, radius_km=50):
    """Returns True if the two lat/lon points are within the given radius."""
    if None in (lat1, lon1, lat2, lon2):
        return False
    try:
        return geodesic((lat1, lon1), (lat2, lon2)).kilometers <= radius_km
    except Exception:
        return False

def get_event_data_near_city(city_name, state_code, event_type, storm_data_dir, radius_km=50):
    """
    Scans NOAA storm data CSVs and returns a dictionary:
    {date: {damage_property: X, injuries: Y, etc}} for events near the specified city.
    """
    city_name = city_name.lower()
    state_code = state_code.upper()

    # Get city coordinates using geopy
    geolocator = Nominatim(user_agent="event_locator", timeout=10)
    location = geolocator.geocode(f"{city_name}, {state_code}, USA")
    if not location:
        print(f"Could not geocode city: {city_name}, {state_code}")
        return {}

    city_coords = (location.latitude, location.longitude)
    print(f"City coordinates: {city_coords}")

    files = glob(os.path.join(storm_data_dir, "*.csv"))
    results = {}

    for file in files:
        print(file)
        with open(file, encoding='latin1') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get('EVENT_TYPE', '').lower() != event_type.lower():
                    continue
                if row.get('STATE', '').upper() != state_code:
                    continue

                try:
                    lat = float(row['BEGIN_LAT'])
                    lon = float(row['BEGIN_LON'])
                except:
                    continue

                if not haversine_within_radius(city_coords[0], city_coords[1], lat, lon, radius_km):
                    continue
                #print("found match!")
                try:
                    year = int(row['BEGIN_YEARMONTH'][:4])    # '2025'
                    month = int(row['BEGIN_YEARMONTH'][4:])   # '06'
                    day = int(row['BEGIN_DAY'])
                    date = datetime(year, month, day)
                    # if date.year==2065:
                    #     print(date.year==2065)

                except:
                    continue

                if date not in results:
                    results[date] = {
                        "damage_property": row.get("DAMAGE_PROPERTY", "0"),
                        "damage_crops": row.get("DAMAGE_CROPS", "0"),
                        "injuries_direct": row.get("INJURIES_DIRECT", "0"),
                        "injuries_indirect": row.get("INJURIES_INDIRECT", "0"),
                        "deaths_direct": row.get("DEATHS_DIRECT", "0"),
                        "deaths_indirect": row.get("DEATHS_INDIRECT", "0"),
                        "event_description": row.get("EVENT_NARRATIVE", "")
                    }

    return results

# Example usage:
storm_event_data = get_event_data_near_city(
    city_name="Houston",
    state_code="TEXAS",
    event_type="Thunderstorm Wind",
    storm_data_dir="data",  # Folder containing all CSVs
    radius_km=75
)
print(len(storm_event_data))
# Show first few:
for date, data in list(storm_event_data.items())[:5]:
    print("printing")
    print(f"{date}: {data}")

print("done")
