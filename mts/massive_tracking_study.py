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
from adblockparser import AdblockRules

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

def append_to_file(file_path, text):
    with open(file_path, 'a') as file:
        file.write(text)

# 3. Fingerprinting
#  From  paper 'iqbal2020fingerprinting', we extract a list of certified browser fingerprinting script hashes obtained through ML. We compare those values and obtain that.
keys = [b'onpointerleave',b'StereoPannerNode',b'FontFaceSetLoadEvent',b'PresentationConnection',b'AvailableEvent',
        b'msGetRegionContent',b'peerIdentity',b'MSManipulationEvent',b'VideoStreamTrack',b'mozSetImageElement',
        b'requestWakeLock',b'audioWorklet',b'onwebkitanimationiteration',b'onpointerenter',b'onwebkitanimationstart',
        b'onlostpointercapture',b'ongotpointercapture',b'onpointerout',b'onafterscriptexecute',b'channelCountMode',
        b'onpointerover',b'onbeforescriptexecute',b'onicegatheringstatechange',b'MediaDevices',b'numberOfInputs',
        b'channelInterpretation',b'speedOfSound',b'dopplerFactor',b'midi',b'ondeviceproximity',b'HTMLMenuItemElement',
        b'updateCommands',b'exportKey']

def get_remote_md5_sum(url, max_file_size=100*1024*1024):
    remote = urllib.request.urlopen(url)
    hash = hashlib.md5()

    total_read = 0
    detected_finger = False
    while not detected_finger:
        data = remote.read(4096)
        total_read += 4096

        if not data or total_read > max_file_size:
            break

        for key in keys:
            if key in data:
                detected_finger = True
                break
        
        hash.update(data)

    if not detected_finger:
        return hash.hexdigest()
    else:
        return True

def detect_fingerprinting(data, fingerprinting_domains):
    found = False
    for beacon in data['beacons']:
        if '.js' in beacon['url']:
            try:
                result = get_remote_md5_sum(beacon['url'])
                if result == True:
                    found = True
                    break
                else:
                    if result in fingerprinting_domains:
                        found = True
                        break
            except Exception as e:
                pass
    return found

def get_last_parts(base_url):

    if base_url.startswith('http://'):
        base_url = base_url[len('http://'):]
    elif base_url.startswith('https://'):
        base_url = base_url[len('https://'):]

    # Split the base URL into parts
    #parts = base_url.split('.')

    #if len(parts) >= 4:
        # Get the last 'a.b.c' substring
        #base_url = '.'.join(parts[-4:])

    if "/" in base_url:
        last_substring_nobars = base_url.split('/')[0]
        return last_substring_nobars
    else:
        return base_url
   
def process_web(web_id, web_url, results_path, error_path, cookies_url_path, beacons_path, fingerprinting_domains):

    try:
        # First check if file with web_id exist and has been processed successfully.
        results_file = results_path+'/'+web_id+'.csv'
        error_file = error_path+'/'+web_id+'.csv'
        wec_out_dir = "wec_out_"+web_id
        if os.path.exists(results_file):
            # Ignore this web, already processed (online).
            return
        elif os.path.exists(error_file):
            # Ignore this web, already processed (error).
            return

        # Check if the website is online and if it uses HTTPS or HTTP protocol.
        protocol = check_url_protocol(web_url)
        if protocol == 0:
            raise Exception("Website not online")
        full_web_url = protocol+"://"+web_url
        protocol_text = "1" if protocol == "https" else "0"

        # Process WEC.
        command = "website-evidence-collector "+full_web_url+" --max 1 --page-timeout 5000 --headless true --output "+wec_out_dir+" 2> /dev/null"
        process = subprocess.Popen(command, shell=True)
        # Wait for the process to complete or timeout
        result = process.communicate(timeout=30)
        exit_code = process.returncode
        inspector_file = wec_out_dir+'/inspection.json'

        # If WEC unsuccessful, then skip
        if not os.path.exists(inspector_file):
            if os.path.exists(wec_out_dir):
                shutil.rmtree(wec_out_dir)
            raise Exception("Error in WEC or Inspector file not found")
        if exit_code != 0:
            if os.path.exists(wec_out_dir):
                shutil.rmtree(wec_out_dir)
            raise Exception("Error in WEC")

        # Open WEC inspection and save cookies and beacons data.
        with open(inspector_file) as f:
            data = json.load(f)

        # Get fingerprinting
        use_fingerprinting = "1" if detect_fingerprinting(data, fingerprinting_domains) else "0"

        # Filter cookies to only get ones that suspect tracking from easyprivacy filter.
        easyprivacy = open('../data/easyprivacy.txt', 'r')
        rules = CustomAdblockRules(easyprivacy.readlines(), use_re2=True, max_mem=512*1024*1024, supported_options=[],skip_unsupported_rules=False)

        tracking_cookies = set()
        for cookie in data["cookies"]:
            if "log" in cookie and "stack" in cookie["log"] and len(cookie["log"]["stack"]) > 0 and "fileName" in cookie["log"]["stack"][0]: 
                filename = cookie["log"]["stack"][0]["fileName"]
            else:
                filename = cookie["domain"]

            tracking_string = rules.should_block(filename)
            if tracking_string:
                filename = get_last_parts(filename)
                if filename not in tracking_cookies:
                    tracking_cookies.add(filename)
        n_cookies = len(tracking_cookies)

        # Check beacons.
        n_beacons = 0
        beacon_list = set()
        for beacon in data["beacons"]:
            if "listName" in beacon and beacon["listName"] == "easyprivacy.txt" and "url" in beacon and beacon["url"] not in beacon_list:
                n_beacons += 1
                beacon_list.add(get_last_parts(beacon["url"]))

        # Write the results in the files.
        append_to_file(results_file, protocol_text+','+str(n_cookies)+','+str(n_beacons)+','+use_fingerprinting+'\n')
        with file_lock:
            for beacon in beacon_list:
                append_to_file(beacons_path+'/'+beacon+'.csv', web_id+',')
            for cookie in tracking_cookies:
                append_to_file(cookies_url_path+'/'+cookie+'.csv', web_id+',')

        # Remove inspection dir.
        shutil.rmtree(wec_out_dir)
    except subprocess.TimeoutExpired:
        # Indicate error.
        append_to_file(error_file, 'T\n')

        process.terminate()
        try:
            # Wait for the process to terminate
            result = process.communicate(timeout=2)
        except subprocess.TimeoutExpired:
            # Kill the process if it doesn't terminate gracefully
            process.kill()
            result = process.communicate()
        if os.path.exists(wec_out_dir):
            shutil.rmtree(wec_out_dir)
        #sys.stderr.write(str(web_id) + '\n')
        #sys.stderr.write(str(e) + '\n')
    except Exception as e:  
        # Indicate error.
        append_to_file(error_file, 'E\n')

        if os.path.exists(wec_out_dir):
            shutil.rmtree(wec_out_dir)
        #sys.stderr.write(str(web_id) + '\n')
        #sys.stderr.write(str(e) + '\n')

    return

def read_csv_to_list(file_path):
    data_list = []
    with open(file_path, mode='r', newline='') as file:
        csv_reader = csv.reader(file)
        for row in csv_reader:
            if row:  # Check if the row is not empty
                data_list.append(row)
    return data_list

def process_chunk(queue, results_path, error_path, cookies_url_path, beacons_path, fingerprinting_domains, chunk):
    sys.stdout = io.StringIO()
    sys.stderr = io.StringIO()
    for web_id, web_url in chunk:
        process_web(web_id, web_url, results_path, error_path, cookies_url_path, beacons_path, fingerprinting_domains)
    output = sys.stdout.getvalue()
    queue.put(output)
    output = sys.stderr.getvalue()
    queue.put(output)

    sys.stdout = sys.__stdout__
    sys.stderr = sys.__stderr__

def start_parallel_work(data_list, results_path, error_path, cookies_url_path, beacons_path, fingerprinting_domains, num_processes):

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
        p = multiprocessing.Process(target=process_chunk, args=(queue, results_path, error_path, cookies_url_path, beacons_path, fingerprinting_domains, chunk))
        processes.append(p)
        p.start()

    for p in processes:
        p.join()

    # Collect and print all outputs
    while not queue.empty():
        output = queue.get()
        print(output, end='')

class CustomAdblockRules(AdblockRules):

    def should_block(self, url, options=None):
        options = options or {}
        if self._is_whitelisted(url, options):
            return False
        res_blacklisted = self._is_blacklisted(url, options)
        if res_blacklisted:
            return res_blacklisted
        return False
    
    def _domain_variants(domain):
        parts = domain.split('.')
        if len(parts) == 1:
            yield parts[0]
        else:
            for i in range(len(parts), 1, -1):
                yield ".".join(parts[-i:])
    
    def _matches(self, url, options,
                 general_re, domain_required_rules, rules_with_options):
        """
        Return if ``url``/``options`` are matched by rules defined by
        ``general_re``, ``domain_required_rules`` and ``rules_with_options``.

        ``general_re`` is a compiled regex for rules without options.

        ``domain_required_rules`` is a {domain: [rules_which_require_it]}
        mapping.

         ``rules_with_options`` is a list of AdblockRule instances that
        don't require any domain, but have other options.
        """
        general_re_res = general_re.search(url)
        if general_re and general_re_res:
            return general_re_res.group()
        return False

if __name__ == '__main__':

    # Path to your CSV file.
    csv_file_path = sys.argv[1]

    # Number of processes to run in parallel (number of cores)
    num_processes = int(sys.argv[2])

    # Web results path.
    results_path = 'results'
    error_path = 'errors'
    cookies_url_path = 'results_cookies'
    beacons_path = 'results_beacons'
    os.makedirs(results_path, exist_ok=True)
    os.makedirs(error_path, exist_ok=True)
    os.makedirs(cookies_url_path, exist_ok=True)
    os.makedirs(beacons_path, exist_ok=True)

    # Open list of fingerprint domains.
    with open('../data/fingerprinting_domains.json') as f:
        fingerprinting_domains = json.load(f)

    fingerprinting_domains = set(fingerprinting_domains.keys())

    data_list = read_csv_to_list(csv_file_path)

    #data_list = data_list[:200]

    # Parallel processing
    start_parallel_work(data_list, results_path, error_path, cookies_url_path, beacons_path, fingerprinting_domains, num_processes)