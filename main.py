import random
from datetime import datetime, timedelta
from openai import OpenAI
from dotenv import load_dotenv
import os
import post_disaster

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Random date range in 2024
def get_random_dates():
    start_day = random.randint(1, 200)# start from day 1 of the year to day whatever, i chose 200
    start_date = datetime(2024, 1, 1) + timedelta(days=start_day)
    end_date = start_date + timedelta(days=random.randint(2, 4))
    return start_date, end_date

# Generate dummy weather data
def generate_dummy_data(start_date, end_date):
    weather_keys = ['rain-inches', 'wind-mph', 'damage-scale', 'power-outages', 'flood-depth-ft']
    descriptors = {
        'damage': ['none', 'minor', 'moderate', 'severe'],
    }

    how_long = (end_date - start_date).days + 1
    data = []

    # Random data points for the days
    # I used uniform because it supposedly chooses numbers mire equally
    for i in range(how_long):
        date = (start_date + timedelta(days=i)).strftime("%b-%d-%Y").lower()
        day_data = ""
        for key in weather_keys:
            if key == 'damage':
                val = random.choice(descriptors['damage'])
            elif key == 'rain-inches':
                val = round(random.uniform(0.1, 15.0), 1)
            elif key == 'wind-mph':
                val = random.randint(5, 100)
            elif key == 'power-outages':
                val = random.randint(0, 10000)
            elif key == 'flood-depth-ft':
                val = round(random.uniform(0.0, 6.0), 1)
            day_data = day_data + f"{date}_{key}: {val}"
        day_data = day_data+". "
        data.append(day_data)
    
    return '\n'.join(data)

# Ring up openai to generate report
def generate_report():
    prompt, weather_data, disasters, city_dict = post_disaster.create_prompt()
    response = client.chat.completions.create( #once we use actual data, ask chat gpt to use public articles/opinions and stuff
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a scientific analyst that specializes in meteorology."},
            {"role": "user", "content": prompt}
        ],
    )

    return response.choices[0].message.content, weather_data, disasters, city_dict

if __name__ == "__main__":
    report = generate_report()
    print("AI-Generated Report using starting date and ending date values:\n")
    print(report)
