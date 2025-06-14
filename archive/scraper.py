#not in use

import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
import geopy
from geopy.distance import geodesic
from geopy.geocoders import Nominatim
from utility_files import json_cache
load_dotenv()

def get_lat_lon(city_name):
    city_name = city_name.lower()
    geolocator = Nominatim(user_agent="Weatherthing", timeout=5)
    attempt_find_value = json_cache.find_value("stationlocation", city_name)
    if attempt_find_value is None:
        location = geolocator.geocode(city_name + ", USA")
        if location is None:
            raise ValueError(f"Location '{city_name}' not found.")
        stored_location = (location.latitude, location.longitude)
        print("Storing location")
        json_cache.store_value("stationlocation", city_name, stored_location)
        #print("lat-lon of city", location.latitude, location.longitude)
        return location.latitude, location.longitude
    else:
        return attempt_find_value

def get_station_near_location(token, lat, lon, start_date, end_date):
    print("given lat/lon:", lat, lon)
    url = "https://www.ncei.noaa.gov/cdo-web/api/v2/stations"
    headers = {"token": token}
    params = {
        "datasetid": "GHCND",
        "limit": 10,
        "latitude": lat,
        "longitude": lon,
        "sortfield": "datacoverage",
        "sortorder": "desc"
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code != 200:
        print(f"[ERROR] Failed to get station: {response.status_code} - {response.text}")
        return None, None

    try:
        data = response.json()
    except requests.exceptions.JSONDecodeError:
        print(f"[ERROR] Response is not JSON. Raw content:\n{response.text}")
        return None, None

    stations = data.get("results", [])
    if not stations:
        print("[INFO] No stations found.")
        return None, None

    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    end_dt = datetime.strptime(end_date, "%Y-%m-%d")

    best_station = None
    best_distance = float('inf')

    for station in stations:
        print("test station id", station['id'])
        try:
            min_date = datetime.strptime(station['mindate'], "%Y-%m-%d")
            max_date = datetime.strptime(station['maxdate'], "%Y-%m-%d")

            if min_date <= start_dt and max_date >= end_dt:
                
                station_coords = (station['latitude'], station['longitude'])
                city_coords = (lat, lon)
                distance_km = geodesic(city_coords, station_coords).kilometers

                if distance_km < best_distance:
                    best_station = station
                    best_distance = distance_km
        except Exception as e:
            print(f"[WARN] Skipping station due to error: {e}")
    print("nearest station:", best_station['latitude'], best_station['longitude'])
    if best_station:
        print(f"Using station: {best_station['id']} - {best_station['name']}")
        print(f"Distance from city: {best_distance:.2f} km")
        return best_station['id'], best_distance

    print("[INFO] No station found covering full date range.")
    return None, None


def fetch_weather_data(token, cityname, start_date, end_date):
    lat, lon = get_lat_lon(cityname)
    station_id, distance_km = get_station_near_location(token, lat, lon, start_date, end_date)
    station_id="GHCND:USW00012960"
    if not station_id:
        print("No station found.")
        return []

    cache_key = f"{station_id}"
    weather_cache = json_cache.find_value("weather_data", cache_key) or {}

    new_data = []
    current_date = datetime.strptime(start_date, "%Y-%m-%d")
    end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")

    while current_date <= end_date_obj:
        date_str = current_date.strftime("%Y-%m-%d")
        if date_str in weather_cache:
            print(f"Using cached data for {date_str}")
            new_data.append(weather_cache[date_str])
        else:
            print(f"Fetching new data for {date_str}")
            url = "https://www.ncei.noaa.gov/cdo-web/api/v2/data"
            headers = {'token': token}
            print(station_id)
            
            params = {
                'datasetid': 'GHCND',
                'stationid': station_id,
                'startdate': date_str,
                'enddate': date_str,
                'limit': 1000,
                'units': 'standard'
            }

            response = requests.get(url, headers=headers, params=params)
            if response.status_code == 200:
                result = response.json().get('results', [])
                weather_cache[date_str] = result
                new_data.append(result)
            else:
                print(f"Failed to fetch data for {date_str}: {response.status_code} - {response.text}")

        current_date += timedelta(days=1)
    print("weather cache:")
    print(weather_cache)
    print(cache_key)
    json_cache.store_value("weather_data", cache_key, weather_cache)
    print("saved")
    return new_data, distance_km

if __name__ == "__main__":
    NOAA_TOKEN = os.getenv("NOAA_API_KEY")
    start_date = '2024-09-12'
    end_date = '2024-09-16'
    city_name = "Houston"
    try:
        weather_data, distance_km = fetch_weather_data(NOAA_TOKEN, city_name, start_date, end_date)
        print("Station used was", distance_km, "km away from specified coordinates.")
        for daily_entries in weather_data:
            for entry in daily_entries:
                date = entry.get('date', 'N/A')
                datatype = entry.get('datatype', 'N/A')
                value = entry.get('value', 'N/A')
                print(f"{date} - {datatype}: {value}")
    except:
        print("Can't find data")
