import os
import pandas as pd
import glob
import heapq
import json
import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt

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

n_websites = 1050286

# Dicts
cookie_dict = {}
beacon_dict = {}

# Initialize an empty min-heap
top_100_cookies = []
top_100_beacons = []

file_path = 'robots.json'

# Read JSON data from a file
with open(file_path, 'r') as file:
    data = json.load(file)

# Iterate over the dictionary
robots_dict = {}
for key, value in data.items():
    robots_dict[key.split('/')[-1]] = value

# Function to maintain top 100
def add_to_top_100(heap, name, num):
    if len(heap) < 100:
        # If fewer than 100, add directly to the heap
        heapq.heappush(heap, (num, name))
    else:
        # If 100, replace the smallest if current is larger
        heapq.heappushpop(heap, (num, name))

csv_cookie_files = glob.glob('./results_cookies/*.csv')
csv_beacon_files = glob.glob('./results_beacons/*.csv')

for file in csv_cookie_files:
    base_filename_with_extension = os.path.basename(file)
    base_filename = os.path.splitext(base_filename_with_extension)[0]

    domain_array = base_filename.split(".")
    if len(domain_array) >= 2:
        domain = ".".join(domain_array[-2:])
    else:
        domain = ".".join(domain_array)
    if domain not in cookie_dict:
        cookie_dict[domain] = set()

    # Read results.
    df = pd.read_csv(file, header=None)
    
    # Extract the first row and its number of websites.
    for website in df.iloc[0][:-1]:
        website = str(int(website))
        if website not in cookie_dict[domain]:
            if website not in robots_dict or robots_dict[website] == '0':
                cookie_dict[domain].add(website)
            

for file in csv_beacon_files:
    base_filename_with_extension = os.path.basename(file)
    base_filename = os.path.splitext(base_filename_with_extension)[0]

    domain_array = base_filename.split(".")
    if len(domain_array) >= 2:
        domain = ".".join(domain_array[-2:])
    else:
        domain = ".".join(domain_array)
    if domain not in beacon_dict:
        beacon_dict[domain] = set()

    # Read results.
    df = pd.read_csv(file, header=None)
    
    # Extract the first row and its number of websites.
    for website in df.iloc[0][:-1]:
        website = str(int(website))
        if website not in beacon_dict[domain]:
            if website not in robots_dict or robots_dict[website] == '0':
                beacon_dict[domain].add(website)

for domain, cookie_set in cookie_dict.items():
    add_to_top_100(top_100_cookies, domain, len(cookie_set)*100/n_websites)
for domain, beacon_set in beacon_dict.items():
    add_to_top_100(top_100_beacons, domain, len(beacon_set)*100/n_websites)

top_100_cookies = sorted(top_100_cookies, reverse=True)[:20]
top_100_beacons = sorted(top_100_beacons, reverse=True)[:20]
print(top_100_cookies)
print(top_100_beacons)

    
    


