import argparse
import post_disaster

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('--eventtype', type=str, required=True, help='Type of weather event to analyze')
    parser.add_argument('--city', type=str, help='City to analyze')
    args = parser.parse_args()
    print(args)
    prompt, weather_data, disasters, city_dict = post_disaster.create_prompt(args.eventtype, args.city)
    print(prompt)