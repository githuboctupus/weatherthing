import csv
import requests
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()
NOAA_TOKEN = os.getenv("NOAA_API_KEY")


def get_top_cities_in_state(state_name, csv_path="uscities.csv", top_n=5):
    top_cities = []

    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        cities = [row for row in reader if row["state_name"].lower() == state_name.lower() and row["population"]]

        for city in cities:
            city["population"] = int(float(city["population"]))

        top_cities = sorted(cities, key=lambda x: x["population"], reverse=True)[:top_n]

    return top_cities

def load_isd_history(file_path="isd-history.csv"):
    stations = []
    with open(file_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Filter for US stations and USAF codes starting with USW, USS, COOP
            if row['CTRY'] == 'US' and row['ICAO'].startswith('K'):
                try:
                    begin_date = datetime.strptime(row['BEGIN'], '%Y%m%d')
                    end_date = datetime.strptime(row['END'], '%Y%m%d')
                    coverage_days = (end_date - begin_date).days
                except Exception:
                    continue

                stations.append({
                    'USAF': row['USAF'],
                    'WBAN': row['WBAN'],
                    'ID': row['USAF'],  # Use USAF as unique ID for station
                    'NAME': row['STATION NAME'],
                    'STATE': row['STATE'],
                    'LAT': float(row['LAT']) if row['LAT'] else None,
                    'LON': float(row['LON']) if row['LON'] else None,
                    'BEGIN': begin_date,
                    'END': end_date,
                    'coverage_days': coverage_days
                })
    return stations



def find_best_station_for_city(city_name, state_code, stations):
    city_name = city_name.lower()
    #print(city_name)
    state_code = state_code.upper()
    #print(state_code)
    # Filter stations in the same state, with city name substring match
    candidate_stations = [
        s for s in stations
        if s['STATE'] == state_code and city_name.upper() in s['NAME']
    ]

    if not candidate_stations:
        # fallback: stations in the same state only
        candidate_stations = [s for s in stations if s['STATE'] == state_code]

    # Sort by coverage_days desc, then closest distance if lat/lon available
    candidate_stations.sort(key=lambda s: s['coverage_days'], reverse=True)

    return candidate_stations[0] if candidate_stations else None


def find_desired_station():
    state_input = input("Enter a state name: ")
    top_cities = get_top_cities_in_state(state_input)

    print(f"\nTop {len(top_cities)} cities in {state_input} by population:")
    for i, city in enumerate(top_cities, 1):
        print(f"{i}. {city['city']} ({city['population']:,}) - {city['state_id']}")

    print("\nLoading ISD station history...")
    isd_stations = load_isd_history("isd-history.csv")

    geolocator = Nominatim(user_agent="weatherthing", timeout=10)

    print("\nFinding best weather stations for each city based on ISD history...")
    cities_stations = []
    for city in top_cities:
        best_station = find_best_station_for_city(city['city'], city['state_id'], isd_stations)

        if best_station:
            # Calculate distance between city centroid and station, if city geocoded
            location = geolocator.geocode(f"{city['city']}, {city['state_id']}, USA")
            distance_km = None
            if location and best_station['LAT'] and best_station['LON']:
                city_coords = (location.latitude, location.longitude)
                station_coords = (best_station['LAT'], best_station['LON'])
                distance_km = geodesic(city_coords, station_coords).kilometers

            print(f"\nBest station for {city['city']}:")
            print(f"Station Name: {best_station['NAME']}")
            cities_stations.append(best_station)
            print(f"Coverage: {best_station['BEGIN'].date()} to {best_station['END'].date()} ({best_station['coverage_days']} days)")
            #print(f"USAF-WBAN: {best_station['USAF']}-{best_station['WBAN']}")
            if distance_km is not None:
                print(f"Distance from city center: {distance_km:.2f} km")
        else:
            print(f"No suitable station found for {city['city']}")
    for i in range(len(top_cities)):
        print((1+i), "-", top_cities[i]['city'])
    citychoice = int(input("Enter the number of the city that you want to analyze the weather patterns of: "))
    stationchoice = cities_stations[citychoice-1]
    print(stationchoice)
    return (stationchoice['LAT'], stationchoice['LON'])
    
