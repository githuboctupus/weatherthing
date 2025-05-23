import random
import openai
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

# Load API key from .env
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Generate random date range in 2024
def get_random_dates():
    start_day = random.randint(1, 300)
    start_date = datetime(2024, 1, 1) + timedelta(days=start_day)
    end_date = start_date + timedelta(days=random.randint(3, 10))
    return start_date.strftime("%B %d, %Y"), end_date.strftime("%B %d, %Y")

# Dummy raw data
dummy_data = """
On April 15th, 2024, Houston experienced severe thunderstorms that brought 6 inches of rain in under 12 hours. 
Localized flooding caused significant disruption, with over 150 homes reporting damage in Harris County. 
Emergency services responded to 23 high-water rescues.

Later in July, a heatwave struck the Houston area, pushing temperatures above 105°F for 5 consecutive days. 
This led to at least 8 reported heat-related hospitalizations and strained the local energy grid, resulting in rolling blackouts.
"""

# Call OpenAI to summarize and analyze
def generate_report(location: str, date_range: str, raw_data: str):
    prompt = f"""
You are a scientific analyst. Write a professional summary of weather-related damage in {location} between {date_range}.

Here is the raw data:
{raw_data}

Your report should summarize major events and provide quantitative analysis if available. Include total damage, event types, and impact on population or infrastructure. Use 2–3 concise paragraphs.
"""

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a scientific analyst."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3
    )
    return response['choices'][0]['message']['content']

# Main execution
if __name__ == "__main__":
    start, end = get_random_dates()
    date_range = f"{start} to {end}"
    location = "Houston, Texas"
    
    print(f"\n📍 Report for {location} from {date_range}\n")
    report = generate_report(location, date_range, dummy_data)
    print(report)
