#this the main backend scripts that work provided you have the tokens for NOAA API and OPENAI

import random
from datetime import datetime, timedelta
from openai import OpenAI
from dotenv import load_dotenv
import os
import post_disaster

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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
