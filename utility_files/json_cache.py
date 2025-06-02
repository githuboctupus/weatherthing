#use this so that we don't have to rely on scanning through massive csv files or txt files
#but currently scanning csv files are pretty fast
#it's just the GHCND_stations.txt that takes a while to scan

import json
import os
from geopy.geocoders import Nominatim
import requests
def load_cache(CACHE_FILE):
    if os.path.exists("utility_files/"+CACHE_FILE+".json"):
        with open("utility_files/"+CACHE_FILE+".json", 'r') as f:
            return json.load(f)
    return {}#can't find

def save_cache(CACHE_FILE, cache):
    with open("utility_files/"+CACHE_FILE+".json", 'w') as f:
        json.dump(cache, f, indent=4)

def find_value(filename, key):
    cache = load_cache(filename)
    if key in cache:
        return cache[key]
    return None # can't find value

def store_value(filename, key, value):
    cache = load_cache(filename)
    if key not in cache:
        cache[key]=value
        save_cache(filename, cache)
        return True
    return False # key already in there
