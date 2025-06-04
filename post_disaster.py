import os
import requests
from datetime import datetime, timedelta
from extract_disaster_data import get_event_data_near_city
from snippettest import load_ghcnd_stations, find_closest_ghcnd_station
from geopy.geocoders import Nominatim
import cityfinder

# Load NOAA API token from environment
NOAA_TOKEN = os.getenv("NOAA_API_KEY")

def scrape_ghcnd_data(station_id, start_date, end_date, token):
    """
    Accesses NOAA API for the GHCND dataset (raw observations per day).
    Returns a dict: {date: {datatype: value}}.
    """
    headers = {"token": token}
    url = "https://www.ncei.noaa.gov/cdo-web/api/v2/data"
    params = {
        "datasetid": "GHCND",
        "stationid": f"GHCND:{station_id}",
        "startdate": start_date,
        "enddate": end_date,
        "limit": 1000,
        "units": "metric",
        "format": "json"
    }

    try:
        response = requests.get(url, headers=headers, params=params, timeout=20)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"Error accessing raw GHCND data: {e}")
        return {}

    observations = {}
    for item in data.get("results", []):
        date = item["date"][:10]
        datatype = item["datatype"]
        value = item["value"]

        if date not in observations:
            observations[date] = {}
        observations[date][datatype] = value

    return observations

def analyze_recent_disasters_weather(event_type, storm_data_dir, top_n=10):
    # Step 1: Get recent disaster events
    lat, lon, city_dict = cityfinder.find_desired_station()
    disasters = get_event_data_near_city(city_dict['city'], city_dict['state_name'].upper(), event_type, storm_data_dir)#TEXAS
    sorted_disasters = sorted(disasters.items(), key=lambda x: x[0], reverse=True)[:top_n]

    if not sorted_disasters:
        print("No disasters found for this configuration.")
        return
    
    print("analyze:", lat, lon)
    closest_station = find_closest_ghcnd_station(lat, lon)
    station_id = closest_station['id']
    print(station_id)
    #quit()
    # Step 3: Analyze post-disaster weather
    for date, info in sorted_disasters:
        start = (date + timedelta(days=1)).strftime("%Y-%m-%d")
        end = (date + timedelta(days=7)).strftime("%Y-%m-%d")
        weather_data = scrape_ghcnd_data(station_id, start, end, NOAA_TOKEN)
        for date, metrics in weather_data.items():
            print(f"📅 {date}:")
            for dtype, val in metrics.items():
                print(f"   • {dtype} = {val}")

# Example usage:
if __name__ == "__main__":
    # Customize these as needed:
    analyze_recent_disasters_weather(
        event_type="Thunderstorm",
        storm_data_dir="data",  # Folder with NOAA CSVs
        top_n=10
    )
