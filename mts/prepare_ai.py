import os
import pandas as pd
import glob
import json
import numpy as np
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

n_files = 0
n_https = 0
n_finger = 0
n_use_cookies = 0
n_use_beacons = 0
total_cookies = 0
total_beacons = 0
mean_cookies = 0.0
mean_beacons = 0.0

number_of_cookies_array = []
number_of_beacons_array = []

number_of_cookies_accept_array = []
number_of_beacons_accept_array = []

# Initialize an empty min-heap
top_100_website_cookies = []
top_100_website_beacons = []

# Tops from Tranco IDs
top_100_ids_cookies = []
top_100_ids_beacons = []
top_100_ids_finger = []

# result object
results_obj = {}

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

def append_to_file(file_path, text):
    with open(file_path, 'a') as file:
        file.write(text)
    
# Path to the JSON file
file_path = 'robots.json'

# Read JSON data from a file
with open(file_path, 'r') as file:
    data = json.load(file)

# Iterate over the dictionary
robots_dict = {}
for key, value in data.items():
    robots_dict[key.split('/')[-1]] = value

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

    # Check if can process.
    if base_filename not in robots_dict or robots_dict[base_filename] == '0':

        results_obj[base_filename] = {}
        results_obj[base_filename]["url"] = domain

        # Read website results.
        df = pd.read_csv(file, header=None)

        # Processed results.
        n_files += 1

        if df.iloc[0][0] == 1: 
            results_obj[base_filename]["scheme"] = "https://"
        else:
            results_obj[base_filename]["scheme"] = "http://"

        append_to_file("sample_ai.csv", base_filename+','+domain+','+str(df.iloc[0][0])+'\n')
    i += 1

    #if i == 10000:
    #    break

print("[OK] Successfully processed websites:",n_files)