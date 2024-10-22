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

csv_cookies = glob.glob('./results_cookies/*.csv')
csv_beacons = glob.glob('./results_beacons/*.csv')

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
    
# Function to maintain top 100 domains
def add_website_to_top_100(heap, website_name, num):
    if len(heap) < 10:
        # If fewer than 50 websites, add directly to the heap
        heapq.heappush(heap, (num, website_name))
    else:
        # If 50 websites, replace the smallest if current is larger
        heapq.heappushpop(heap, (num, website_name))

# result object
cookie_dict = {}
beacon_dict = {}
results_obj = {}
n_files = 0
top_100_websites_cookies = []
top_100_websites_beacons = []

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

def count_commas_in_file(file_path):
    comma_count = 0
    chunk_size = 1024 * 1024  # 1 MB chunks

    with open(file_path, 'r') as file:
        while chunk := file.read(chunk_size):
            comma_count += chunk.count(',')

    return comma_count

def csv_string_to_set(file_path):
    with open(file_path, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            # Convert comma-separated string to a set
            result_set = set(row)
            # Removing empty strings if any (caused by trailing commas)
            result_set.discard('')
            return result_set
        
def process_last_part(last_part):
    if last_part in ["googletagmanager.com","google-analytics.com","google.com","doubleclick.net","google.es","googlesyndication.com","googleadservices.com","googleapis.com","youtube.com","gstatic.com","googleoptimize.com"]:
        last_part = "Google LLC"
    elif "yandex" in last_part:
        last_part = "Yandex LLC" 
    elif last_part in ["facebook.net","facebook.com"]:
        last_part = "Meta Platforms, Inc."
    elif last_part in ["bing.com","clarity.ms"]:
        last_part = "Microsoft Corporation"
    elif last_part in ["linkedin.com","licdn.com"]:
        last_part = "LinkedIn Corporation"
    elif last_part in ["bitrix.info"]:
        last_part = "Bitrix24"
    elif last_part in ["hs-analytics.net","hsforms.com","hubspot.com"]:
        last_part = "HubSpot"
    elif last_part in ["tiktok.com"]:
        last_part = "ByteDance"
    elif last_part in ["mail.ru","vk.com"]:
        last_part = "VK" 
    elif last_part in ["twitter.com","t.co"]:
        last_part = "Twitter (X)" 
    elif last_part in ["demdex.net","everesttech.net","adobedtm.com","typekit.net"]:
        last_part = "Adobe" 
    elif last_part in ["hotjar.com"]:
        last_part = "Contentsquare"
    elif last_part in ["wp.com"]:
        last_part = "Automattic Inc."
    elif last_part in ["ad-delivery.net","cloudflareinsights.com","btloader.com"]:
        last_part = "Cloudflare, Inc."
    elif last_part in ["trustarc.com"]:
        last_part = "Domains By Proxy, LLC"
    elif last_part in ["webvisor.org"]:
        last_part = "INTERSEARCH SOLUTIONS LLC"
    elif last_part in ["yadro.ru"]:
        last_part = "Yadro"
    elif last_part in ["klaviyo.com"]:
        last_part = "Klaviyo, Inc."
    elif last_part in ["pinterest.com"]:
        last_part = "Pinterest, Inc."
    elif last_part in ["shopifysvc.com"]:
        last_part = "Shopify"
    elif last_part in ["nr-data.net"]:
        last_part = "New Relic"
    
    return last_part

file_path = 'robots.json'

# Read JSON data from a file
with open(file_path, 'r') as file:
    data = json.load(file)

# Iterate over the dictionary
robots_dict = {}
robots_set = set()
for key, value in data.items():
    robots_dict[key.split('/')[-1]] = value
    if value == "1":
        robots_set.add(key.split('/')[-1])

# Process tranco list.
file_path = 'tranco.csv'
dict_ids = csv_to_dict(file_path)

domains = set([".co.uk",".co.jp",".co.nz",".com.au",".co.za",".co.in",".com.mx",".co.kr",".com.cn",".com.sg",".com.br",".org.uk",".com.my"])

for file in csv_cookies:

    base_filename_with_extension = os.path.basename(file)
    base_filename = os.path.splitext(base_filename_with_extension)[0]
    last_part = ".".join(base_filename.split('.')[-2:])
    if "."+last_part in domains:
        last_part = ".".join(base_filename.split('.')[-3:])

    last_part = process_last_part(last_part)

    cookie_set = csv_string_to_set('./results_cookies/'+base_filename_with_extension)
    cookie_set.difference_update(robots_set)

    if last_part in cookie_dict:
        cookie_dict[last_part] = cookie_dict[last_part] | cookie_set
    else:
        cookie_dict[last_part] = cookie_set

for file in csv_beacons:

    base_filename_with_extension = os.path.basename(file)
    base_filename = os.path.splitext(base_filename_with_extension)[0]
    last_part = ".".join(base_filename.split('.')[-2:])
    if "."+last_part in domains:
        last_part = ".".join(base_filename.split('.')[-3:])

    last_part = process_last_part(last_part)

    beacons_set = csv_string_to_set('./results_beacons/'+base_filename_with_extension)
    beacons_set.difference_update(robots_set)

    if last_part in beacon_dict:
        beacon_dict[last_part] = beacon_dict[last_part] | beacons_set
    else:
        beacon_dict[last_part] = beacons_set

for domain, website_set in cookie_dict.items():
    add_website_to_top_100(top_100_websites_cookies, domain, len(website_set))

for domain, website_set in beacon_dict.items():
    add_website_to_top_100(top_100_websites_beacons, domain, len(website_set))

sumat = 1050286
top_100_websites_cookies_per = []
total_cookies = 0
for item in top_100_websites_cookies:
    total_cookies += item[0]
    text = item[1] + " & " + str(round(item[0]*100/sumat,1)) + "% ("+str(item[0])+")"
    top_100_websites_cookies_per.append(text)
top_100_websites_beacons_per = []
total_beacons = 0
for item in top_100_websites_beacons:
    total_beacons += item[0]
    text = item[1] + " & " + str(round(item[0]*100/sumat,1)) + "% ("+str(item[0])+")"
    top_100_websites_beacons_per.append(text)

results_obj["total_cookies"] = total_cookies
results_obj["total_cookies_per"] = total_cookies*100/sumat
results_obj["total_beacons"] = total_beacons
results_obj["total_beacons_per"] = total_beacons*100/sumat
results_obj["top_100_websites_cookies"] = sorted(top_100_websites_cookies, reverse=True)
results_obj["top_100_websites_beacons"] = sorted(top_100_websites_beacons, reverse=True)
results_obj["top_100_websites_cookies_per"] = top_100_websites_cookies_per
results_obj["top_100_websites_beacons_per"] = top_100_websites_beacons_per

with open('test_topcompanies.json', 'w') as file:
    json.dump(results_obj, file, default=convert_numpy, indent=4)