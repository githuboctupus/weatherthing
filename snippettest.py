
import cityfinder
def load_ghcnd_stations(filepath="GHCND_stations.txt"):
    stations = {}
    with open(filepath, 'r') as file:
        for line in file:
            station_id = line[0:11].strip()
            lat = float(line[12:20].strip())
            lon = float(line[21:30].strip())
            state = line[38:40].strip()
            name = line[41:71].strip()
            stations[station_id] = {
                'id': station_id,
                'lat': lat,
                'lon': lon,
                'state': state,
                'name': name
            }
    return stations

ghcnd_stations = load_ghcnd_stations()

# match based on proximity
from geopy.distance import geodesic

def find_closest_ghcnd_station(lat, lon, ghcnd_stations):
    min_dist = float('inf')
    closest_station = None
    for station in ghcnd_stations.values():
        dist = geodesic((lat, lon), (station['lat'], station['lon'])).km
        if dist < min_dist:
            min_dist = dist
            closest_station = station
    return closest_station

if __name__ == "__main__":
    selected = cityfinder.find_desired_station()
    station = find_closest_ghcnd_station(selected[0], selected[1], load_ghcnd_stations())
    print("done")
    print(f"Closest GHCND station ID: {station['id']}, Name: {station['name']}")
