import os
import pandas as pd
import glob
import heapq
import json
import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt
import csv

colors=[
    "#88CCEE",
    "#CC6677",
    "#DDCC77",
    "#117733",
    "#AA4499",
    "#44AA99",
    "#999933",
    "#882255",
    "#661100",
    "#6699CC",
    "#888888"
]

csv_files = glob.glob('./results/*.csv')

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

# result object
results_obj = {}
n_files = 0
top_10_websites_finger = []
top_10_websites_cookies = []
top_10_websites_beacons = []

# Function to maintain top 50 websites
def add_website_to_top_10(heap, website_name, num):
    if len(heap) < 50:
        # If fewer than 50 websites, add directly to the heap
        heapq.heappush(heap, (-num, website_name))
    else:
        # If 50 websites, replace the smallest if current is larger
        heapq.heappushpop(heap, (-num, website_name))

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

# Process tranco list.
file_path = 'tranco.csv'
dict_ids = csv_to_dict(file_path)

i = 0

for file in csv_files:

    if i % 10000 == 0:
        print(f"Iteration: {i}")

    base_filename_with_extension = os.path.basename(file)
    base_filename = os.path.splitext(base_filename_with_extension)[0]
    domain = dict_ids[base_filename]

    # Read website results.
    df = pd.read_csv(file, header=None)

    # Processed results.
    n_files += 1

    if df.iloc[0][3] == 1: 
        add_website_to_top_10(top_10_websites_finger, domain, int(base_filename))

    if df.iloc[0][1] > 0:
        add_website_to_top_10(top_10_websites_cookies, domain, int(base_filename))

    if df.iloc[0][2] > 0:
        add_website_to_top_10(top_10_websites_beacons, domain, int(base_filename))

    i += 1

    #if i == 20000:
    #    break

results_obj["top_10_websites_finger"] = sorted([(-num_cookies, website) for num_cookies, website in top_10_websites_finger])
results_obj["top_10_websites_cookies"] = sorted([(-num_cookies, website) for num_cookies, website in top_10_websites_cookies])
results_obj["top_10_websites_beacons"] = sorted([(-num_cookies, website) for num_cookies, website in top_10_websites_beacons])

with open('test_top10.json', 'w') as file:
    json.dump(results_obj, file, default=convert_numpy, indent=4)