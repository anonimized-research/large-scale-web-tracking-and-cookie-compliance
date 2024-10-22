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

n_files = 0
n_files_accept = 0
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

# Function to maintain top 100 websites
def add_website_to_top_100(heap, website_name, num, reverse=False):
    if len(heap) < 100:
        # If fewer than 100 websites, add directly to the heap
        if reverse:
            heapq.heappush(heap, (-num, website_name))
        else:
            heapq.heappush(heap, (num, website_name))
    else:
        # If 100 websites, replace the smallest if current is larger
        if reverse:
            heapq.heappushpop(heap, (-num, website_name))
        else:
            heapq.heappushpop(heap, (num, website_name))

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

def manageViolationsTable(df, dict_ids, base_filename, violations_table):
    # Manage violations table
    domain = dict_ids[base_filename]
    parts = domain.rsplit('.', 1)
    domain_last = '.' + parts[1]
    if domain_last in violations_table['total']:
        violations_table['total'][domain_last] += 1
    violations_table['total']['total'] += 1

    if domain_last in violations_table['total']:
        if df.iloc[0][3] == 1:
            # Uses finger
            violations_table['finger'][domain_last] += 1
        if df.iloc[0][1] > 0:
            # Uses track cookies
            violations_table['cookies'][domain_last] += 1
        if df.iloc[0][2] > 0:
            # Uses track beacons
            violations_table['beacons'][domain_last] += 1

    if df.iloc[0][3] == 1:
        # Uses finger
        violations_table['finger']['total'] += 1
    if df.iloc[0][1] > 0:
        # Uses track cookies
        violations_table['cookies']['total'] += 1
    if df.iloc[0][2] > 0:
        # Uses track beacons
        violations_table['beacons']['total'] += 1

    return violations_table


violations_table = {'cookies': {'total': 0, '.de': 0, '.fr': 0, '.it': 0, '.es': 0, '.pl': 0, '.ro': 0, '.nl': 0, '.com': 0}, 'beacons': {'total': 0, '.de': 0, '.fr': 0, '.it': 0, '.es': 0, '.pl': 0, '.ro': 0, '.nl': 0, '.com': 0}, 'finger': {'total': 0, '.de': 0, '.fr': 0, '.it': 0, '.es': 0, '.pl': 0, '.ro': 0, '.nl': 0, '.com': 0}, 'total': {'total': 0, '.de': 0, '.fr': 0, '.it': 0, '.es': 0, '.pl': 0, '.ro': 0, '.nl': 0, '.com': 0}}
    
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

# Get all filenames in the directory
filenames_accept = os.listdir("./results_accept")

accept_list = set([f for f in filenames_accept if os.path.isfile(os.path.join("./results_accept", f))])

i = 0

for file in csv_files:

    if i % 10000 == 0:
        print(f"Iteration: {i}")

    base_filename_with_extension = os.path.basename(file)
    base_filename = os.path.splitext(base_filename_with_extension)[0]
    domain = dict_ids[base_filename]

    # Check if can process.
    if base_filename not in robots_dict or robots_dict[base_filename] == '0':

        # Processed results.
        n_files += 1

        # Now check the number of cookies in the accept website.

        if base_filename_with_extension in accept_list:
            # Read website accept results.
            df_accept = pd.read_csv("./results_accept/"+base_filename_with_extension, header=None)
            if df_accept.iloc[0][4] == 1: 
                n_files_accept += 1

    i += 1

    #if i == 10000:
    #    break

results_obj["n_websites"] = n_files
results_obj["n_websites_accept"] = n_files_accept
    
with open('test_data_accept.json', 'w') as file:
    json.dump(results_obj, file, default=convert_numpy, indent=4)