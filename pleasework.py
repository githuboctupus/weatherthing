import requests
from geopy.distance import geodesic
from dotenv import load_dotenv
from datetime import datetime
import os

load_dotenv()

def fetch_stations_within_radius(token, lat, lon, radius_km=100):
    url = "https://www.ncei.noaa.gov/cdo-web/api/v2/stations"
    headers = {"token": token}
    params = {
        "datasetid": "LCD",
        "latitude": lat,
        "longitude": lon,
        "limit": 100,
        "sortfield": "datacoverage",
        "sortorder": "desc"
    }

    response = requests.get(url, headers=headers, params=params)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch stations: {response.status_code} - {response.text}")

    stations = []
    for station in response.json().get("results", []):
        try:
            station_coords = (station["latitude"], station["longitude"])
            distance_km = geodesic((lat, lon), station_coords).kilometers
            if distance_km <= radius_km:
                stations.append({
                    "id": station["id"],
                    "name": station["name"],
                    "distance_km": round(distance_km, 2)
                })
        except:
            continue

    return stations

def fetch_data_count(token, station_id, start_date, end_date):
    url = "https://www.ncei.noaa.gov/cdo-web/api/v2/data"
    headers = {"token": token}
    params = {
        "datasetid": "LCD",
        "stationid": station_id,
        "startdate": start_date,
        "enddate": start_date,
        "limit": 25,  # Just need the metadata
        "units": "metric"
    }
    
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        data = response.json().get("results", [])
        print(data)
        #print("results", response.get("results", []))
        return len(data)
    return 0

def find_best_station(token, lat, lon, start_date, end_date, radius_km=100):
    stations = fetch_stations_within_radius(token, lat, lon, radius_km)
    if not stations:
        print("No stations found within radius.")
        return None

    best_station = None
    max_data_points = -1

    for station in stations:
        count = fetch_data_count(token, station["id"], start_date, end_date)
        if count > max_data_points:
            max_data_points = count
            best_station = station
            best_station["data_count"] = count

    return best_station

# --- Usage Example ---
if __name__ == "__main__":
    NOAA_TOKEN = os.getenv("NOAA_API_KEY")
    lat, lon = 29.7604, -95.3698  # Houston
    radius_km = 100
    start_date = "2024-09-12"
    end_date = "2024-09-16"

    station = find_best_station(NOAA_TOKEN, lat, lon, start_date, end_date, radius_km)
    if station:
        print(f"Best station in {radius_km} km with most data:")
        print(f"{station['id']} | {station['name']} | {station['distance_km']} km | Data points: {station['data_count']}")
    else:
        print("No suitable station found.")
