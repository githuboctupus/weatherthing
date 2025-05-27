import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
import geopy
from geopy.geocoders import Nominatim
from utility_files import json_cache
load_dotenv()

def get_lat_lon(city_name):
    city_name = city_name.lower()
    geolocator = Nominatim(user_agent="Weatherthing", timeout=5)  # You can name this anything
    attempt_find_value = json_cache.find_value("stationlocation", city_name)
    if attempt_find_value == None:
        location = geolocator.geocode(city_name + ", USA") #in Location object form
        if location == None:
            raise ValueError(f"Location '{city_name}' not found.")
        stored_location = (location.latitude, location.longitude)
        print("storing location")
        json_cache.store_value("stationlocation", city_name, stored_location)
        return location.latitude, location.longitude
    else:
        location = attempt_find_value # in stored_value form, which is tuple form
        return location
    #raise ValueError(f"Location '{city_name}' not found.")

# Example usage:
def get_station_near_location(token, lat, lon):
    url = "https://www.ncei.noaa.gov/cdo-web/api/v2/stations"
    headers = {"token": token}
    params = {
        "datasetid": "GHCND",
        "limit": 5,
        "sortfield": "distance",
        "sortorder": "asc",
        "latitude": lat,
        "longitude": lon
    }

    response = requests.get(url, headers=headers, params=params)
    data = response.json()

    stations = data.get("results", [])
    if not stations: #no stations found which usually wouldn't be ran
        return None

    # Return the closest station's ID
    return stations[0]['id']
def fetch_weather_data(token, cityname, start_date, end_date):
    base_url = "https://www.ncei.noaa.gov/cdo-web/api/v2/data"
    lat, lon = get_lat_lon(cityname)
    station_id = get_station_near_location(token, lat, lon)
    headers = {
        'token': token
    }
    params = {
        'datasetid': 'GHCND',
        'stationid': station_id,
        'startdate': start_date,
        'enddate': end_date,
        'limit': 1000,
        'units': 'standard'
    }

    response = requests.get(base_url, headers=headers, params=params)

    if response.status_code != 200:
        print(f"Error: {response.status_code} - {response.text}")
        return []

    data = response.json().get('results', [])
    return data



if __name__ == "__main__":
    NOAA_TOKEN = os.getenv("NOAA_API_KEY")
    STATION_ID = 'GHCND:USW00012918'  #Houston Intercontinental Airport, is there a way to find ID using location name?

    start_date = '2024-09-12'
    end_date = '2024-09-16'

    # weather_data = fetch_weather_data(NOAA_TOKEN, STATION_ID, start_date, end_date)

    # for entry in weather_data:
    #     date = entry.get('date', 'N/A')
    #     datatype = entry.get('datatype', 'N/A')
    #     value = entry.get('value', 'N/A')
    #     print(f"{date} - {datatype}: {value}")
    get_lat_lon("houstoN")
    get_lat_lon("chicago")