import json
import matplotlib.pyplot as plt
import numpy as np


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

translation_dict = {
    'Empresa i Finances': 'Business and Finance',
    'Ciència, Tecnologia, Enginyeria i Matemàtiques': 'Science and Technology',
    'Videojocs': 'Video Games',
    'Ocupació': 'Employment',
    'Joc i Apostes': 'Gambling and Betting',
    'Literatura, Art i Cultura': 'Arts and Culture',
    'Compres': 'Shopping',
    'Religió i Espiritualitat': 'Religion and Spirituality',
    'Notícies': 'News',
    'Lleis, Govern i Política': 'Law and Politics',
    'Salut': 'Health',
    'Moda i Estil': 'Fashion',
    'Viatges i Turisme': 'Travel',
    'Jardineria i Plantes': 'Gardening',
    'Esport': 'Sports',
    'Menjar i Alimentació': 'Food and Nutrition',
    'Educació': 'Education',
    'Adults': 'Adults',
    'Animals i Mascotes': 'Animals and Pets',
    'Música': 'Music',
    'Habitatge': 'Housing',
    'Automoció': 'Automotive',
    'Xarxes Socials': 'Social Media',
}

# Read the JSON file
with open('ai_res.json', 'r', encoding='utf-8') as file:
    data = json.load(file)  # Load the JSON data into a Python object

# Print the resulting object
print(data["cat_webs"].keys())
print(len(data["cat_webs"].keys()))

# Print keys and the length of the array of values for each key
for key, value in data["cat_webs"].items():
    if isinstance(value, list):  # Check if the value is a list
        length = len(value)
    else:
        length = 0  # If it's not a list, we can consider its length as 0 or handle it as needed
    print(f"Key: '{key}', Length of value array: {length}")

# Example data
data_dict = data["cat_webs"]
del data_dict['NaN']
del data_dict['Xarxes Socials']
new_data_dict = {translation_dict.get(k, k): v for k, v in data_dict.items()}
categories = list(new_data_dict.keys())  # category names
counts = [len(ids) for ids in new_data_dict.values()]  # number of IDs per category

# Sort categories and counts by counts in descending order
sorted_pairs = sorted(zip(counts, categories), reverse=False)  # sort by counts (first element in pair)
counts_sorted, categories_sorted = zip(*sorted_pairs)  # unzip the sorted pairs
print(categories_sorted)

# Horizontal bar plot
plt.figure(figsize=(10, 6))
bars = plt.barh(categories_sorted, counts_sorted, color='#88CCEE')
for bar in bars:
    if bar.get_width() > 5000:
        x = bar.get_width()-5000
    else:
        x = bar.get_width()+300
    plt.text(x, bar.get_y() + bar.get_height()/2, 
             str(bar.get_width()), va='center', ha='left')
plt.xlabel('Number of websites', fontsize=16)
plt.tight_layout()
plt.savefig('img_categories.pdf', format="PDF", bbox_inches='tight')

total_websites = 1050286
nan = 0
categorized = 0
social_media = 0
single_category = 0
multiple_category = 0
for website_id, category_dict in data["webs"].items():
    if len(category_dict.keys()) == 1 and "NaN" in category_dict:
        nan += 1
    elif "Xarxes Socials" in category_dict:
        social_media += 1
    else:
        categorized += 1
        if len(category_dict.keys()) > 1:
            if len(category_dict.keys()) > 2:
                print(category_dict.keys())
            multiple_category += 1
        else:
            single_category += 1

print("Categorized:", categorized)
print("Single, Double:", single_category, multiple_category)
print("Single, Double (%):", single_category/categorized*100, multiple_category/categorized*100)
print("NaN:",nan)
print("Social Media:",social_media)
print("Errors:",total_websites-nan-categorized)

# Now violations table for each category.

# Read the JSON file
with open('../results_merged.json', 'r', encoding='utf-8') as file:
    data_results = json.load(file)  # Load the JSON data into a Python object

violations_table = {}
violations_table["total"] = {"cookies":0,"beacons":0,"finger":0}
total = 0
for website_id, results in data_results.items():
    if website_id in data["webs"]:
        categories = data["webs"][website_id].keys()
    else:
        categories = ["Error"]
    for category in categories:
        total += 1
        if category not in violations_table:
            violations_table[category] = {"cookies":0,"beacons":0,"finger":0}
        if results[1] > 0:
            violations_table[category]["cookies"] += 1
            violations_table["total"]["cookies"] += 1
        if results[2] > 0:
            violations_table[category]["beacons"] += 1
            violations_table["total"]["beacons"] += 1
        if results[3] > 0:
            violations_table[category]["finger"] += 1
            violations_table["total"]["finger"] += 1


violations_table_per = {}
total_dict = {}
for category, results in violations_table.items():
    if category == "total":
        cat_name = "total"
        total_len = total
    elif category == "NaN":
        cat_name = "NaN"
        total_len = nan
    elif category == "Xarxes Socials":
        cat_name = translation_dict[category]
        total_len = social_media
    elif category == "Error":
        cat_name = "Error"
        total_len = total_websites-nan-categorized
    else:
        total_len = len(data["cat_webs"][category])
        cat_name = translation_dict[category]

    violations_table_per[cat_name] = {
        'cookies': round(results['cookies']/total_len*100,2),
        'beacons': round(results['beacons']/total_len*100,2),
        'finger': round(results['finger']/total_len*100,2)
    }

    total_dict[cat_name] = total_len

percentages_cookies = []
percentages_beacons = []
percentages_finger = []
occurrences = []
for category in categories_sorted[::-1]:
    percentages_cookies.append(violations_table_per[category]["cookies"])
    percentages_beacons.append(violations_table_per[category]["beacons"])
    percentages_finger.append(violations_table_per[category]["finger"])
    occurrences.append(total_dict[category])

wm_cookies = round(sum(p * w for p, w in zip(percentages_cookies, occurrences)) / sum(occurrences),2)
wm_beacons = round(sum(p * w for p, w in zip(percentages_beacons, occurrences)) / sum(occurrences),2)
wm_finger = round(sum(p * w for p, w in zip(percentages_finger, occurrences)) / sum(occurrences),2)

percentages_cookies_ord = sorted(percentages_cookies, reverse=False)
percentages_beacons_ord = sorted(percentages_beacons, reverse=False)
percentages_finger_ord = sorted(percentages_finger, reverse=False)

unsorted_data = []
for category in categories_sorted[::-1]:
    violations = violations_table_per[category]
    index_cookies = percentages_cookies_ord.index(violations["cookies"])
    index_beacons = percentages_beacons_ord.index(violations["beacons"])
    index_finger = percentages_finger_ord.index(violations["finger"])
    cookies_per = round(100/22*index_cookies,2)
    beacons_per = round(100/22*index_beacons,2)
    finger_per = round(100/22*index_finger,2)
    mean_per = cookies_per+beacons_per+finger_per/3
    unsorted_data.append([category,mean_per])
    violations_table_per[category]["cookies_per"] = cookies_per
    violations_table_per[category]["beacons_per"] = beacons_per
    violations_table_per[category]["finger_per"] = finger_per

sorted_data = sorted(unsorted_data, key=lambda x: x[1], reverse=True)

for category,mean_per in sorted_data:
    violations = violations_table_per[category]
    print("\\textbf{"+category+"} & \cellcolor{red!"+str(violations["cookies_per"])+"}"+str(violations["cookies"])+"\% & \cellcolor{red!"+str(violations["beacons_per"])+"}"+str(violations["beacons"])+"\% & \cellcolor{red!"+str(violations["finger_per"])+"}"+str(violations["finger"])+"\% & "+str(total_dict[category])+" \\\\")
    print("\hline")

print("\hline")
print("\\textbf{Weighted Mean} & "+str(wm_cookies)+"\% & "+str(wm_beacons)+"\% & "+str(wm_finger)+"\% & "+str(sum(occurrences))+" \\\\")
print("\hline")

with open('violation_table_cat.json', 'w') as file:
    json.dump(violations_table_per, file, default=convert_numpy, indent=4)
    