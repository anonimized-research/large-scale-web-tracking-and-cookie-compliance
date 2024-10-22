import os
import json
import csv
import glob
import pandas as pd
import numpy as np

csv_files = glob.glob('./results/*.csv')

n_files = 0
n_http = 0
n_https = 0
n_robots = 0

# result object
results_obj = {}

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

    # Read website results.
    df = pd.read_csv(file, header=None)

    # Processed results.
    n_files += 1

    if base_filename in robots_dict and robots_dict[base_filename] == '1':
        n_robots += 1
    else:
        if df.iloc[0][0] == 1: 
            n_https += 1
        else:
            n_http += 1

    i += 1

    #if i == 20000:
    #    break

results_obj["n_websites"] = n_files
results_obj["n_https"] = n_https
results_obj["n_http"] = n_http
results_obj["n_robots"] = n_robots

with open('test_data_success.json', 'w') as file:
    json.dump(results_obj, file, default=convert_numpy, indent=4)

print(results_obj)

