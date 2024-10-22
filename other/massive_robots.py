import csv
import requests
import os
import urllib
import hashlib
import subprocess
import json
import shutil
import time
import threading
import multiprocessing
import sys
import io
from pathlib import Path
from multiprocessing import Process, Manager
from urllib.error import URLError
from urllib.parse import urlparse, urljoin
from fake_useragent import UserAgent
import urllib.robotparser

# Configure logging
#logging.basicConfig(filename='progress.log', level=logging.INFO, format='%(asctime)s - %(message)s')

# Global file lock
file_lock = threading.Lock()

def time_elapsed_decorator(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Time elapsed: {elapsed_time:.6f} seconds")
        return result
    return wrapper

def read_csv_to_dict(file_path):
    data_dict = {}
    with open(file_path, mode='r', newline='') as file:
        csv_reader = csv.reader(file)
        for row in csv_reader:
            if row:  # Check if the row is not empty
                data_dict[row[0]] = row[1]
    return data_dict

def append_to_file(file_path, text):
    with open(file_path, 'a') as file:
        file.write(text)
        
# Function to check if web scraping is allowed for a certain URL
def can_scrape(url, user_agent, protocol_char):

    try:
        # Step 1: Get website root and robots.txt url.
        if protocol_char == '1':
            website_root = 'https://'+url
        else:
            website_root = 'http://'+url
        robots_url = website_root+"/robots.txt"

        # Step 2: Try fetch the robots.txt file and extract text.
        response = requests.get(robots_url, timeout=(1,3))
        robots_txt_content = response.text

        # Step 3: Initialize the RobotFileParser object and parse the robots.txt content
        rp = urllib.robotparser.RobotFileParser()
        rp.parse(robots_txt_content.splitlines())

        # Step 4: Check if a specific user agent can access the URL
        return rp.can_fetch(user_agent, website_root)
    except requests.exceptions.SSLError as e:
        if protocol_char == '1':
            return can_scrape(url, user_agent, '0')
        return True
    except Exception as e:
        return True

def process_web(web_id, web_url, origin_path, robots_path):

    # First check if file with web_id exist and has been processed successfully.
    origin_file = origin_path+'/'+web_id+'.csv'
    robots_file = robots_path+'/'+web_id+'.csv'
    if os.path.exists(robots_file):
        # Ignore this web, already processed.
        return
    
    with open(origin_file, 'r') as file:
        protocol_char = file.read(1)
    
    # Check the robots.txt.

    # Initialize the UserAgent object
    ua = UserAgent()
    # Get a random User-Agent
    user_agent = ua.random

    if can_scrape(web_url, user_agent, protocol_char):
        append_to_file(robots_file, '0\n')
    else:
        append_to_file(robots_file, '1\n')

    return

def read_csv_to_list(file_path):
    data_list = []
    with open(file_path, mode='r', newline='') as file:
        csv_reader = csv.reader(file)
        for row in csv_reader:
            if row:  # Check if the row is not empty
                data_list.append(row)
    return data_list

def process_chunk(queue, csvs_dir, robots_path, web_dict, chunk):
    sys.stdout = io.StringIO()
    sys.stderr = io.StringIO()
    for web_id_filename in chunk:
        web_id = Path(web_id_filename).stem
        web_url = web_dict[web_id]
        process_web(web_id, web_url, csvs_dir, robots_path)
    output = sys.stdout.getvalue()
    queue.put(output)
    output = sys.stderr.getvalue()
    queue.put(output)

    sys.stdout = sys.__stdout__
    sys.stderr = sys.__stderr__

def start_parallel_work(data_list, csvs_dir, robots_path, web_dict, num_processes):

    # Create a queue to share data between processes
    queue = multiprocessing.Queue()

    # Split the data list into chunks for each process
    chunk_size = len(data_list) // num_processes
    chunks = [data_list[i:i + chunk_size] for i in range(0, len(data_list), chunk_size)]

    # If the number of chunks exceeds num_processes, adjust the last chunk
    if len(chunks) > num_processes:
        chunks[-2].extend(chunks[-1])
        chunks = chunks[:-1]

    processes = []
    for chunk in chunks:
        #reversed_chunk = chunk[::-1]
        p = multiprocessing.Process(target=process_chunk, args=(queue, csvs_dir, robots_path, web_dict, chunk))
        processes.append(p)
        p.start()

    for p in processes:
        p.join()

    # Collect and print all outputs
    while not queue.empty():
        output = queue.get()
        print(output, end='')

if __name__ == '__main__':

    # Path to your CSVS dir.
    csvs_dir = './results'

    # Number of processes to run in parallel (number of cores).
    num_processes = int(sys.argv[1])

    # Web results path.
    robots_path = './robots'
    os.makedirs(robots_path, exist_ok=True)

    # Get all filenames in the directory
    filenames = os.listdir(csvs_dir)

    # Filter out directories, only include files
    data_list = [f for f in filenames if os.path.isfile(os.path.join(csvs_dir, f))]

    #data_list = data_list[:20]

    web_dict = read_csv_to_dict('tranco.csv')

    # Parallel processing
    start_parallel_work(data_list, csvs_dir, robots_path, web_dict, num_processes)