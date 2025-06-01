import os
import pandas as pd
import gzip
import io
import requests

def load_storm_data(year):
    cache_dir = "data/"
    os.makedirs(cache_dir, exist_ok=True)
    filename = f"{cache_dir}StormEvents_details_{year}.csv"
    
    if not os.path.exists(filename):
        print(f"Downloading {year}...")
        url = f"https://www.ncei.noaa.gov/pub/data/swdi/stormevents/csvfiles/StormEvents_details-ftp_v1.0_d{year}_c20250520.csv.gz"
        r = requests.get(url)
        with gzip.GzipFile(fileobj=io.BytesIO(r.content)) as f_in:
            with open(filename, 'wb') as f_out:
                f_out.write(f_in.read())
    
    return pd.read_csv(filename, low_memory=False)
# for i in range(75):
#     try:
#         load_storm_data(1950+i)
#     except:
#         print(1950+i, "year doesn't have gzip")
local_path_csv = os.path.join("data", "StormEvents_details_1951.csv")
r = requests.get("https://www.ncei.noaa.gov/pub/data/swdi/stormevents/csvfiles/StormEvents_details-ftp_v1.0_d1951_c20250401.csv.gz", timeout=20)
if r.status_code == 200:

    with open(local_path_csv, 'wb') as f:
        f.write(r.content)