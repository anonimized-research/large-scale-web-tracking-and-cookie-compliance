import os
import json

if __name__ == '__main__':

    # Path to your CSVS dir.
    csvs_dir = './robots'

    # Get all filenames in the directory
    filenames = os.listdir(csvs_dir)

    # Filter out directories, only include files
    robots_list = set([f for f in filenames if os.path.isfile(os.path.join(csvs_dir, f))])

    res_dict = {}
    for file in robots_list:
        # Read first char of file.
        with open("./robots/"+file, 'r') as file:
            first_char = file.read(1)
        res_dict[file.name.replace(".csv","")] = first_char

# Writing dictionary to a JSON file
with open("robots.json", "w") as json_file:
    json.dump(res_dict, json_file)


    

    