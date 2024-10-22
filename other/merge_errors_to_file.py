import os
import json

if __name__ == '__main__':

    # Path to your CSVS dir.
    csvs_dir = './errors'

    # Web results path.
    newerror_dir = './new_errors'

    # Get all filenames in the directory
    filenames = os.listdir(csvs_dir)

    # Filter out directories, only include files
    error_list = set([f for f in filenames if os.path.isfile(os.path.join(csvs_dir, f))])

    # Get all filenames in the directory
    filenames = os.listdir(newerror_dir)

    # Filter out directories, only include files
    newerror_list = set([f for f in filenames if os.path.isfile(os.path.join(newerror_dir, f))])

    res_dict = {}
    for file in error_list:
        if file in newerror_list:
            file_dir = newerror_dir
        else:
            file_dir = csvs_dir
        # Read first char of file.
        with open(file_dir+'/'+file, 'r') as file:
            first_char = file.read(1)
        res_dict[file.name.replace(".csv","")] = first_char

# Writing dictionary to a JSON file
with open("errors.json", "w") as json_file:
    json.dump(res_dict, json_file)