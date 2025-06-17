from bottle import route, run, request, static_file
import json
from datetime import datetime
import cityfinder

@route('/')
def index():
    return static_file('index.html', root='.')

@route('/static/<filename>')
def send_static(filename):
    return static_file(filename, root='./static')

@route('/get_cities', method='POST')
def get_cities():
    data = request.json
    state = data.get('state')
    # You would replace this with your real function
    cities = get_top_cities(state)
    return json.dumps(cities)

@route('/get_disaster_data', method='POST')
def get_data():
    data = request.json
    city = data.get('city')
    disaster = data.get('disaster')
    result = get_disaster_data(city, disaster)
    return json.dumps(result, default=str)

# -----------------------------
# Replace these with your real logic:
def get_top_cities(state):
    # Example dummy data
    top_cities = cityfinder.get_top_cities_in_state(state)
    returnme = ""
    for i in range(len(top_cities)):
        returnme+=str(i+1)+ "."+ top_cities[i]['city']+ "\n"
    print("ran")
    return [{"index": i + 1, "city": city["city"]} for i, city in enumerate(top_cities)]

    return returnme

def get_disaster_data(city, disaster):
    return {
        "summary": f"Disasters in {city} related to {disaster}:",
        "events": [
            [datetime(2024, 7, 8), {
                "damage": 0.0,
                "injuries": 0,
                "deaths": 1,
                "event_description": "Floodwaters drowned a motorist.",
                "importance": 1000.0
            }]
        ],
        "weather_data": {
            "2024-07-09": {"AWND": 1.8, "PRCP": 0.0, "RHAV": 71, "TAVG": 27.9}
        }
    }

run(host='localhost', port=8080, debug=True)
