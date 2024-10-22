import csv
import os
import subprocess
import multiprocessing
import sys
import io
import uuid
import re
import pickle
import web_scrapping
from model_multilabel import BertForMultiLabelSequenceClassification
from transformers import BertTokenizer
from googletrans import Translator
import requests
import torch
import warnings
from sklearn.exceptions import InconsistentVersionWarning

# Suppress the InconsistentVersionWarning
warnings.filterwarnings("ignore", category=InconsistentVersionWarning)

# Load the MultiLabelBinarizer
with open('label_encoder.pkl', 'rb') as f:
    mlb = pickle.load(f)

# Get the list of label names
label_names = mlb.classes_.tolist()

def append_to_file(file_path, text):
    with open(file_path, 'a') as file:
        file.write(text)

# Function to read regex rules from a file and compile them.
def read_regex_rules(file_path):
    regex_rules = []
    
    # Open the file in read mode
    with open(file_path, 'r') as file:
        # Read each line in the file
        for line in file:
            # Strip any leading/trailing whitespace (including newlines)
            rule = line.strip()
            
            # If the line is not empty, compile the regex and add it to the list
            if rule:
                compiled_regex = re.compile(rule)
                regex_rules.append(compiled_regex)
    
    return regex_rules

# Function to check a URL against the regex rules
def is_url_matching(url, regex_rules):
    for regex in regex_rules:
        if regex.match(url):
            return True
    return False
   
def process_web(web_id, web_url, scheme, uuid_str, regex_rules, results_path, error_path, chromedriver_path, model, tokenizer):

    try:
        # First check if file with web_id exist and has been processed successfully.
        results_file = results_path+'/'+web_id+'.csv'
        error_file = error_path+'/'+web_id+'.csv'
        if os.path.exists(results_file):
            # Ignore this web, already processed (online).
            return
        elif os.path.exists(error_file):
            # Ignore this web, already processed (error).
            return

        # Check if url is social network.
        if is_url_matching(web_url, regex_rules):
            append_to_file(results_file, 'Xarxes Socials,[1]\n')
            print("Classificació determinada: Xarxes Socials")
            return

        # Extract the text from URL.
        if str(scheme) == "0":
            url = "http://"+web_url
        else:
            url = "https://"+web_url
        text = web_scrapping.extract_text_from_url(url, uuid_str, error_file, chromedriver_path)
        if text is None or text == "" or text.isspace(): 
            append_to_file(error_file, 'Cannot retrieve text\n')
            return

        # Process and translate text.
        text = re.sub(r'[^a-zA-Z0-9\sÀ-ÿ$€£"%Δ.,/\'\-<>?!()@\’\‘]', ' ', text)
        text = text.lower()
        text = re.sub(r'\s+', ' ', text)

        translator = Translator()
        # Split text into chunks of up to 5000 characters (limit size for translator)
        max_chunk_size = 5000
        chunks = [text[i:i + max_chunk_size] for i in range(0, len(text), max_chunk_size)]
        
        translated_text = ""
        # Using a session to ensure proper closure of connections
        with requests.Session() as session:
            for chunk in chunks:
                detected = translator.detect(chunk)
                if detected.lang not in ["ca", "es", "en"]:
                    translation = translator.translate(chunk, dest='en')
                    translated_text += translation.text
                else:
                    translated_text += chunk

        print(" - Translated text")
        
        inputs = tokenizer(translated_text, truncation=True, padding='max_length', max_length=512, return_tensors='pt')
        
        # Make prediction
        outputs = model(**inputs)
        #token_pred_end_time = time.time()  # End time measurement for tokenization and prediction
        # The model returns a tuple. The actual predictions are the first item in the tuple.
        predictions = outputs[0]
        
        # Multi Label behavior
        # Apply sigmoid function to get "probabilities" / confidence values
        probabilities = torch.sigmoid(predictions[0])
        
        # Get the values and indices of the top predictions
        top_probs, top_indices = torch.topk(probabilities, 6)
        
        # Get the names of the top predicted labels
        top_labels = [label_names[index] for index in top_indices]
    
        # Filter labels with probability >= 0.5
        predicted_labels = [label for label, prob in zip(top_labels, top_probs) if prob >= 0.5]
        
        # Convert the list to a string and print without brackets
        predicted_category = ";".join([item for item in predicted_labels if item is not None])
        if not predicted_category:
            predicted_category = "NaN"
        print(f"Classificació determinada: {predicted_category}")
        filtered_probs = [prob.item() for prob in top_probs if prob >= 0.5]  # Convert tensors to floats and filter
        print(f"Confiança de cada categoria: {filtered_probs}") # Where filtered probs contains top_probs.tolist() but filtered

        append_to_file(results_file, predicted_category+','+str(filtered_probs)+'\n')
        return
        
    except Exception as e:  
        # Indicate error.
        if e is None:
            append_to_file(error_file, 'E\n')
        else:
            append_to_file(error_file, 'E\n')
            append_to_file(error_file, str(e))
        

    print()
    return

def read_csv_to_list(file_path):
    data_list = []
    with open(file_path, mode='r', newline='') as file:
        csv_reader = csv.reader(file)
        for row in csv_reader:
            if row:  # Check if the row is not empty
                data_list.append(row)
    return data_list

def process_chunk(queue, regex_rules, results_path, error_path, chromedriver_path, chunk):

    # Process I/O
    sys.stdout = io.StringIO()
    sys.stderr = io.StringIO()

    # Generate a random UUID (version 4)
    uuid_str = str(uuid.uuid4())

    # Load the AI models and tokenizers.
    model = BertForMultiLabelSequenceClassification.from_pretrained('../data/_bert_model_multi_final')
    tokenizer = BertTokenizer.from_pretrained('bert-base-multilingual-cased', clean_up_tokenization_spaces=True)

    # Process each website in the chunk.
    for web_id, web_url, scheme in chunk:
        print(web_url, web_id, ":")
        try:
            process_web(web_id, web_url, scheme, uuid_str, regex_rules, results_path, error_path, chromedriver_path, model, tokenizer)
        except Exception as e:
            if e is None:
                print(web_id, web_url, "Exception at main:")
            else:
                print(web_id, web_url, "Exception at main:")
                print(e)

    # Process I/O
    output = sys.stdout.getvalue()
    queue.put(output)
    output = sys.stderr.getvalue()
    queue.put(output)
    sys.stdout = sys.__stdout__
    sys.stderr = sys.__stderr__

    return

def start_parallel_work(data_list, regex_rules, results_path, error_path, chromedriver_path, num_processes):

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
        p = multiprocessing.Process(target=process_chunk, args=(queue, regex_rules, results_path, error_path, chromedriver_path, chunk))
        processes.append(p)
        p.start()

    for p in processes:
        p.join()

    # Collect and print all outputs
    while not queue.empty():
        output = queue.get()
        print(output, end='')

if __name__ == '__main__':

    # Path to your CSV file.
    csv_file_path = sys.argv[1]

    chromedriver_path = sys.argv[2]

    # Number of processes to run in parallel (number of cores)
    num_processes = int(sys.argv[3])

    # Web results path.
    results_path = 'results_ai'
    error_path = 'errors_ai'
    os.makedirs(results_path, exist_ok=True)
    os.makedirs(error_path, exist_ok=True)

    data_list = read_csv_to_list(csv_file_path)

    #data_list = data_list[:100]

    # Social networks.
    regex_rules = read_regex_rules("../data/social_networks.txt")

    # Parallel processing
    start_parallel_work(data_list, regex_rules, results_path, error_path, chromedriver_path, num_processes)