import os
import json
import ast

result_data = {}
res_dict = {}
categories_dict = {}
categories_web_dict = {}

# Path to your CSVS dir.
csvs_dir = './results_ai'

# Get all filenames in the directory
filenames = os.listdir(csvs_dir)

# Filter out directories, only include files
ai_list = set([f for f in filenames if os.path.isfile(os.path.join(csvs_dir, f))])

for file in ai_list:
    # Read first char of file.
    with open("./results_ai/"+file, 'r') as file:
        try:
            # Process CSV
            website_id = file.name.replace(".csv","").rpartition('/')[-1]
            first_line = file.readline().strip()
            first_line_split = first_line.split(",[", 1)
            if len(first_line_split) > 1:
                first_line_split[1] = "[{}".format(first_line_split[1])
            array_categories = first_line_split[0].split(";")

            if array_categories[0] == 'NaN':
                array_probs = [0]
            else:
                array_probs = ast.literal_eval(first_line_split[1])
            
            # Iterate in pairs
            res_dict[website_id] = {}
            for category, probs in zip(array_categories, array_probs):
                if category not in categories_dict:
                    categories_dict[category] = []
                    categories_web_dict[category] = []
                categories_dict[category].append(probs)
                categories_web_dict[category].append(website_id)
                res_dict[website_id][category] = probs
        except Exception as e:
            print(e)
            print(website_id)
            print(first_line)
            print(first_line_split)
            print(array_categories, array_probs)
            exit()

result_data["webs"] = res_dict
result_data["cat_probs"] = categories_dict
result_data["cat_webs"] = categories_web_dict

# Writing dictionary to a JSON file
with open("ai_res.json", "w", encoding='utf-8') as json_file:
    json.dump(result_data, json_file, ensure_ascii=False)


    

    