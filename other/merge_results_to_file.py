import os
import pandas as pd
import glob
import heapq
import json
import numpy as np
import csv

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

result_dict = {}

i = 0

for file in csv_files:

    if i % 10000 == 0:
        print(f"Iteration: {i}")

    base_filename_with_extension = os.path.basename(file)
    base_filename = os.path.splitext(base_filename_with_extension)[0]
    domain = dict_ids[base_filename]

    # Check if can process.
    if base_filename not in robots_dict or robots_dict[base_filename] == '0':

        # Read website results.
        df = pd.read_csv(file, header=None)

        result_dict[base_filename] = df.iloc[0].values

    i += 1

    #if i == 20000:
    #    break

with open('results_merged.json', 'w') as file:
    json.dump(result_dict, file, default=convert_numpy)