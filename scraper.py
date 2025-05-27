import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
load_dotenv()
def fetch_weather_data(token, station_id, start_date, end_date):
    base_url = "https://www.ncei.noaa.gov/cdo-web/api/v2/data"
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

    weather_data = fetch_weather_data(NOAA_TOKEN, STATION_ID, start_date, end_date)

    for entry in weather_data:
        date = entry.get('date', 'N/A')
        datatype = entry.get('datatype', 'N/A')
        value = entry.get('value', 'N/A')
        print(f"{date} - {datatype}: {value}")