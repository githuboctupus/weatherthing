import os
import requests
from datetime import datetime, timedelta
from extract_disaster_data import get_event_data_near_city
from snippettest import load_ghcnd_stations, find_closest_ghcnd_station
from geopy.geocoders import Nominatim
import cityfinder
import json
import itertools

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

def analyze_recent_disasters_weather(event_type, storm_data_dir, top_n=3):
    # Step 1: Get recent disaster events
    lat, lon, city_dict = cityfinder.find_desired_station()
    disasters = get_event_data_near_city(city_dict['city'], city_dict['state_name'].upper(), event_type, storm_data_dir)#TEXAS
    sorted_disasters = disasters[:top_n]
    #quit()
    if not sorted_disasters:
        print("No disasters found for this configuration.")
        return
    
    print("analyze:", lat, lon, "trying to find closest weather station (non-API)")
    closest_station = find_closest_ghcnd_station(lat, lon)
    station_id = closest_station['id']
    print(station_id)
    #quit()
    # Step 3: Analyze post-disaster weather\
    desired_metrics = {"TMIN", "TMAX", "TAVG", "PRCP", "AWND", "RHAV", "SNWD"}
    filtered_weather = {}
    days_after=4#important variable, analyze n days after storm
    #print(sorted_disasters)
    for date, info in sorted_disasters:
        start = (date + timedelta(days=1)).strftime("%Y-%m-%d")
        end = (date + timedelta(days=days_after)).strftime("%Y-%m-%d")
        weather_data = scrape_ghcnd_data(station_id, start, end, NOAA_TOKEN)

        for date, metrics in weather_data.items():
            #print(date)
            #print(type(date))
            filtered_weather[date] = {k: v for k, v in metrics.items() if k in desired_metrics}
            #print(filtered_weather[date])
            #quit()
            print(f"📅 {date}:")
            for dtype, val in metrics.items():
                if dtype in desired_metrics:
                    print(f"   • {dtype} = {val}")
        
    return city_dict, filtered_weather, sorted_disasters


def create_prompt():
    event_type=input("Enter the event type: ")
    city_dict, weather_data, disasters = analyze_recent_disasters_weather(
        event_type=event_type,
        storm_data_dir="recent_data",  # Folder with NOAA CSVs
        top_n=3
    )
    #print(weather_data)
    prompt = f"You are a scientific analyst/weather expert that is analyzing weather patterns after a {event_type} at {city_dict['city']}. Here is the data on each event in list[datetimeobejct, JSON] format: {disasters}. Here is the post-event data from the NOAA GHCND database in a JSON format:{json.dumps(weather_data)}. Use other sources of info along with the data given to give a report on what is typically seen at this location after the given event, and how consistent these post-disaster patterns are."
    #print(prompt)
    return prompt
# Example usage:
if __name__ == "__main__":
    # Customize these as needed:
    event_type="Flash Flood"
    city_dict, weather_data, disasters = analyze_recent_disasters_weather(
        event_type=event_type,
        storm_data_dir="recent_data",  # Folder with NOAA CSVs
        top_n=3
    )
    print(weather_data)
    prompt = f"You are a scientific analyst/weather expert that is analyzing weather patterns after a {event_type} at {city_dict['city']}. Here is the data on each event in list[datetimeobject, JSON] format: {disasters}. Here is the post-event data from the NOAA GHCND database in a JSON format:{json.dumps(weather_data)}. Use other sources of info along with the data given to give a report on what is typically seen at this location after the given event, and how consistent these post-disaster patterns are."
    print(prompt)


