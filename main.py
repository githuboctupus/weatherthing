import random
from datetime import datetime, timedelta
from openai import OpenAI
from dotenv import load_dotenv
import os

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

    delta = (end_date - start_date).days + 1
    data = []

    # Random data points for the days
    for i in range(delta):
        date = (start_date + timedelta(days=i)).strftime("%b-%d-%Y").lower()
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
            data.append(f"{date}_{key}: {val}")
    
    return '\n'.join(data)

# Call OpenAI to generate report
def generate_report(location: str, date_range: str, raw_data: str):
    prompt = f"""
You are a scientific analyst. Write a concise summary of weather-related damage in {location} between {date_range}.

The data is structured like this:
<date>_<event-type>: <value>

Summarize major weather events, total precipitation, wind speeds, damage levels, and impact on population/infrastructure. Use the data to support your analysis. Use 2–3 short, analytical paragraphs.

Here is the raw data:
{raw_data}
"""

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a scientific analyst that specializes in meteorology."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3
    )

    return response.choices[0].message.content

if __name__ == "__main__":
    location = "Houston, Texas"
    start_date, end_date = get_random_dates()
    date_range = f"{start_date.strftime('%B %d, %Y')} to {end_date.strftime('%B %d, %Y')}"

    raw_data = generate_dummy_data(start_date, end_date)
    raw_data = raw_data.split("\n")
    shortened_data = raw_data[0]+"\n"+raw_data[len(raw_data)-1]

    print(f"\nReport for {location} from {date_range}\n")
    print("Raw Data:\n", shortened_data)#splice for now since chatgpt charges stuff per character

    report = generate_report(location, date_range, raw_data)
    print("AI-Generated Report:\n")
    print(report)
