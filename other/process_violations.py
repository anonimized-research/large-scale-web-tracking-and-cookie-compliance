import json
import matplotlib.pyplot as plt
import numpy as np
import csv

# Convert numpy data types to native Python data types
def convert_numpy(obj):
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    else:
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
    
# Read tranco list to dict.
def csv_to_dict(file_path):
    data_dict = {}
    with open(file_path, mode='r') as csv_file:
        csv_reader = csv.reader(csv_file)
        for row in csv_reader:
            if len(row) == 2:  # Ensure the row has exactly two elements
                key, value = row
                data_dict[key] = value
    return data_dict

# Read the JSON file
with open('results_merged.json', 'r', encoding='utf-8') as file:
    data_results = json.load(file)  # Load the JSON data into a Python object

# Process tranco list.
file_path = 'tranco.csv'
dict_ids = csv_to_dict(file_path)

# Now violations table.
categories = ["total",".de",".fr",".it",".es",".pl",".ro",".nl",".com"]
violations_table = {'cookies': {'total': 0, '.de': 0, '.fr': 0, '.it': 0, '.es': 0, '.pl': 0, '.ro': 0, '.nl': 0, '.com': 0}, 'beacons': {'total': 0, '.de': 0, '.fr': 0, '.it': 0, '.es': 0, '.pl': 0, '.ro': 0, '.nl': 0, '.com': 0}, 'finger': {'total': 0, '.de': 0, '.fr': 0, '.it': 0, '.es': 0, '.pl': 0, '.ro': 0, '.nl': 0, '.com': 0}, 'total': {'total': 0, '.de': 0, '.fr': 0, '.it': 0, '.es': 0, '.pl': 0, '.ro': 0, '.nl': 0, '.com': 0}}

total = 0
for website_id, results in data_results.items():
    domain = dict_ids[website_id]
    parts = domain.rsplit('.', 1)
    domain_last = '.' + parts[1]
    if domain_last in violations_table['total']:
        violations_table['total'][domain_last] += 1
    violations_table['total']['total'] += 1

    if domain_last in violations_table['total']:
        if results[3] > 0:
            # Uses finger
            violations_table['finger'][domain_last] += 1
        if results[1] > 0:
            # Uses track cookies
            violations_table['cookies'][domain_last] += 1
        if results[2] > 0:
            # Uses track beacons
            violations_table['beacons'][domain_last] += 1

    if results[3] > 0:
        # Uses finger
        violations_table['finger']['total'] += 1
    if results[1] > 0:
        # Uses track cookies
        violations_table['cookies']['total'] += 1
    if results[2] > 0 :
        # Uses track beacons
        violations_table['beacons']['total'] += 1

# Percentages violation table.
violations_table["percentage"] = violations_table["total"]
for key in violations_table["total"]:
    for type_m in ["cookies","beacons","finger"]:
        if not type_m+"_per" in violations_table:
            violations_table[type_m+"_per"] = {}
        violations_table[type_m+"_per"][key] = str(round(violations_table[type_m][key] / violations_table["total"][key] * 100, 1))


percentages_cookies = []
percentages_beacons = []
percentages_finger = []
occurrences = []
for category in categories:
    percentages_cookies.append(violations_table["cookies_per"][category])
    percentages_beacons.append(violations_table["beacons_per"][category])
    percentages_finger.append(violations_table["finger_per"][category])
    occurrences.append(violations_table["percentage"][category])

percentages_cookies_ord = sorted(percentages_cookies, reverse=False)
percentages_beacons_ord = sorted(percentages_beacons, reverse=False)
percentages_finger_ord = sorted(percentages_finger, reverse=False)

color_dict = {"cookies_per": {}, "beacons_per": {}, "finger_per":{}}
for category in categories:
    index_cookies = percentages_cookies_ord.index(violations_table["cookies_per"][category])
    index_beacons = percentages_beacons_ord.index(violations_table["beacons_per"][category])
    index_finger = percentages_finger_ord.index(violations_table["finger_per"][category])
    cookies_per = round(100/9*index_cookies,2)
    beacons_per = round(100/9*index_beacons,2)
    finger_per = round(100/9*index_finger,2)
    color_dict["cookies_per"][category] = str(cookies_per)
    color_dict["beacons_per"][category] = str(beacons_per)
    color_dict["finger_per"][category] = str(finger_per)

print()
print("\\cellcolor{red!"+color_dict["cookies_per"]["total"]+"}"+violations_table["cookies_per"]["total"]+"\\% & \\cellcolor{red!"+color_dict["cookies_per"][".de"]+"}"+violations_table['cookies_per'][".de"]+"\\% & \\cellcolor{red!"+color_dict['cookies_per'][".fr"]+"}"+violations_table['cookies_per']['.fr']+"\\% & \\cellcolor{red!"+color_dict['cookies_per']['.it']+"}"+violations_table['cookies_per'][".it"]+"\\% & \\cellcolor{red!"+color_dict['cookies_per']['.es']+"}"+violations_table['cookies_per']['.es']+"\\% & \\cellcolor{red!"+color_dict['cookies_per']['.pl']+"}"+violations_table['cookies_per']['.pl']+"\\% & \\cellcolor{red!"+color_dict['cookies_per']['.ro']+"}"+violations_table['cookies_per']['.ro']+"\\% & \\cellcolor{red!"+color_dict['cookies_per']['.nl']+"}"+violations_table['cookies_per']['.nl']+"\\% & \\cellcolor{red!"+color_dict['cookies_per']['.com']+"}"+violations_table['cookies_per'][".com"]+"\\% \\\\")
print()
print("\\cellcolor{red!"+color_dict["beacons_per"]["total"]+"}"+violations_table["beacons_per"]["total"]+"\\% & \\cellcolor{red!"+color_dict["beacons_per"][".de"]+"}"+violations_table['beacons_per'][".de"]+"\\% & \\cellcolor{red!"+color_dict['beacons_per'][".fr"]+"}"+violations_table['beacons_per']['.fr']+"\\% & \\cellcolor{red!"+color_dict['beacons_per']['.it']+"}"+violations_table['beacons_per'][".it"]+"\\% & \\cellcolor{red!"+color_dict['beacons_per']['.es']+"}"+violations_table['beacons_per']['.es']+"\\% & \\cellcolor{red!"+color_dict['beacons_per']['.pl']+"}"+violations_table['beacons_per']['.pl']+"\\% & \\cellcolor{red!"+color_dict['beacons_per']['.ro']+"}"+violations_table['beacons_per']['.ro']+"\\% & \\cellcolor{red!"+color_dict['beacons_per']['.nl']+"}"+violations_table['beacons_per']['.nl']+"\\% & \\cellcolor{red!"+color_dict['beacons_per']['.com']+"}"+violations_table['beacons_per'][".com"]+"\\% \\\\")
print()
print("\\cellcolor{red!"+color_dict["finger_per"]["total"]+"}"+violations_table["finger_per"]["total"]+"\\% & \\cellcolor{red!"+color_dict["finger_per"][".de"]+"}"+violations_table['finger_per'][".de"]+"\\% & \\cellcolor{red!"+color_dict['finger_per'][".fr"]+"}"+violations_table['finger_per']['.fr']+"\\% & \\cellcolor{red!"+color_dict['finger_per']['.it']+"}"+violations_table['finger_per'][".it"]+"\\% & \\cellcolor{red!"+color_dict['finger_per']['.es']+"}"+violations_table['finger_per']['.es']+"\\% & \\cellcolor{red!"+color_dict['finger_per']['.pl']+"}"+violations_table['finger_per']['.pl']+"\\% & \\cellcolor{red!"+color_dict['finger_per']['.ro']+"}"+violations_table['finger_per']['.ro']+"\\% & \\cellcolor{red!"+color_dict['finger_per']['.nl']+"}"+violations_table['finger_per']['.nl']+"\\% & \\cellcolor{red!"+color_dict['finger_per']['.com']+"}"+violations_table['finger_per'][".com"]+"\\% \\\\")


with open('violation_table.json', 'w') as file:
    json.dump(violations_table, file, default=convert_numpy, indent=4)
    