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
import robotexclusionrulesparser
from urllib.parse import urlparse, urljoin

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

def check_url_protocol(url):
    http_url = f"http://{url}"
    https_url = f"https://{url}"

    # Check HTTPS connection
    try:
        response = requests.get(https_url, timeout=5)
        if response.status_code == 200:
            return "https"
    except requests.RequestException as e:
        try:
            response = requests.get(http_url, timeout=5)
            if response.status_code == 200:
                return "http"
        except requests.RequestException as e:
            return 0
    
    return 0

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

# Function to fetch a URL and store the result in a shared dictionary
def fetch_url(rp, url, return_dict):
    try:
        # Attempt to fetch the URL using the rp.fetch (rp is a RobotExclusionRulesParser instance)
        rp.fetch(url)
        # If successful, mark success in the specified dictionary
        return_dict['success'] = True
    except Exception as e:
        # If there's an error, store the error message in the specified dictionary
        return_dict['error'] = str(e)


# Function to fetch a URL with a timeout mechanism
# Necessary because RobotExclusionRulesParser class doesn't have built-in handling for some errors
def rpFetchWithTimeout(rp, url, timeout=10):
    # Use a Manager to create a shared dictionary for communication between processes
    with Manager() as manager:
        return_dict = manager.dict() # Shared dictionary to store results or errors
        # Create a new process to fetch the URL
        p = Process(target=fetch_url, args=(rp, url, return_dict))
        p.start() # Start the process
        p.join(timeout) # Wait for the process to finish, with a timeout

        # If the process is still alive after the timeout
        if p.is_alive():
            print("Timeout en l'operació de fetch")
            p.terminate() # Terminate the process
            p.join() # Ensure the process has terminated
            raise URLError("Fetch operation timed out") # Raise a timeout error
        # If there was an error during fetching, handle it
        if 'error' in return_dict:
            raise URLError(f"Failed to fetch {url}: {return_dict['error']}")
        
# Function to check if web scraping is allowed for a certain URL
def can_scrape(url, user_agent):
    # Parse the URL to extract the base components (scheme and netloc)
    parsed_url = urlparse(url)
    # Construct the "base" or "main" URL (example: "https://example.com")
    base_url = parsed_url.scheme + "://" + parsed_url.netloc
    # Construct the robots.txt URL (example: "https://example.com/robots.txt")
    robots_url = urljoin(base_url, "/robots.txt")

    # Initialize the robot exclusion rules parser
    rp = robotexclusionrulesparser.RobotExclusionRulesParser()
    # Set the user-agent for the parser
    rp.user_agent = user_agent
    print("Analitzant", robots_url)
    try:
        # Fetch the robots.txt file with a timeout
        rpFetchWithTimeout(rp, robots_url)
    except URLError as e:
        # If fetching fails, show an error and return False
        print(f"No s'ha pogut accedir a {robots_url}")
        return False

    # Check if the URL allows web scraping
    return rp.is_allowed(user_agent, url)

def process_web(web_id, web_url, origin_path, results_path, robots_path):

    # First check if file with web_id exist and has been processed successfully.
    origin_file = origin_path+'/'+web_id+'.csv'
    results_file = results_path+'/'+web_id+'.csv'
    robots_file = robots_path+'/'+web_id+'.csv'
    if os.path.exists(results_file):
        # Ignore this web, already processed.
        return
    
    with open(origin_file, 'r') as file:
        first_char = file.read(1)
    
    if first_char == 'T':
        # Timeout on WEC, leave it that way.
        append_to_file(results_file, 'T\n')
    else:
        # Check if the website is online.
        protocol = check_url_protocol(web_url)
        if protocol == 0:
            # Website offline
            append_to_file(results_file, 'O\n')
        else:
            # Website is online and it was originally an error so leave it that way (WEC error)
            append_to_file(results_file, 'E\n')

    return

def read_csv_to_list(file_path):
    data_list = []
    with open(file_path, mode='r', newline='') as file:
        csv_reader = csv.reader(file)
        for row in csv_reader:
            if row:  # Check if the row is not empty
                data_list.append(row)
    return data_list

def process_chunk(queue, csvs_dir, results_path, robots_path, web_dict, chunk):
    try:
        sys.stdout = io.StringIO()
        sys.stderr = io.StringIO()
        for web_id_filename in chunk:
            web_id = Path(web_id_filename).stem
            web_url = web_dict[web_id]
            process_web(web_id, web_url, csvs_dir, results_path, robots_path)
        output = sys.stdout.getvalue()
        queue.put(output)
        output = sys.stderr.getvalue()
        queue.put(output)

        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
    except Exception as a:
        print(a)

def start_parallel_work(data_list, csvs_dir, results_path, robots_path, web_dict, num_processes):

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
        p = multiprocessing.Process(target=process_chunk, args=(queue, csvs_dir, results_path, robots_path, web_dict, chunk))
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
    csvs_dir = './errors'

    # Number of processes to run in parallel (number of cores).
    num_processes = int(sys.argv[1])

    # Web results path.
    results_path = './new_errors'
    robots_path = './robots'
    os.makedirs(results_path, exist_ok=True)
    os.makedirs(robots_path, exist_ok=True)

    # Get all filenames in the directory
    filenames = os.listdir(csvs_dir)

    # Filter out directories, only include files
    data_list = [f for f in filenames if os.path.isfile(os.path.join(csvs_dir, f))]

    #data_list = data_list[:100]

    web_dict = read_csv_to_dict('tranco.csv')

    # Parallel processing
    start_parallel_work(data_list, csvs_dir, results_path, robots_path, web_dict, num_processes)