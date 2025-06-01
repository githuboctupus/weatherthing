import csv
with open("isd-history.csv", newline='', encoding='utf-8') as f:
    reader = csv.reader(f)
    headers = next(reader)
    print(headers)