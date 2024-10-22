import os
import json

n_we = 0
n_wt = 0
n_o = 0

if __name__ == '__main__':

    # Path to the JSON file
    file_path = 'errors.json'

    # Read JSON data from a file
    with open(file_path, 'r') as file:
        data = json.load(file)

    # Iterate over the dictionary
    for key, value in data.items():
        if value == 'E':
           n_we += 1
        elif value == 'T':
            n_wt += 1
        elif value == 'O':
            n_o += 1
        else:
            print('UNKNOWN!',value)
        #print(f"{key}: {value}")

    print(n_we,n_wt,n_o)
