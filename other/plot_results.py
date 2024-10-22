import json
import numpy as np
import matplotlib.pyplot as plt

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

with open('results_data.json', 'r') as file:
    results_obj = json.load(file)
    
number_of_cookies_array = results_obj["number_of_cookies_array"]
number_of_cookies_accept_array = results_obj["number_of_cookies_accept_array"]
number_of_beacons_array = results_obj["number_of_beacons_array"]
number_of_beacons_accept_array = results_obj["number_of_beacons_accept_array"]

# Plot combined cookie histogram.
max_cookies = 13
n_mean_all = sum(number_of_cookies_array) / len(number_of_cookies_array)
n_mean_accept = sum(number_of_cookies_accept_array) / len(number_of_cookies_accept_array)
bins = np.arange(max_cookies + 2) - 0.5
hist_all, bins = np.histogram(number_of_cookies_array, bins=bins)
hist_percent_all = (hist_all / len(number_of_cookies_array)) * 100
hist_accept, bins = np.histogram(number_of_cookies_accept_array, bins=bins)
hist_percent_accept = (hist_accept / len(number_of_cookies_accept_array)) * 100
plt.figure(figsize=(10, 6))
plt.bar(np.arange(max_cookies + 1) - 0.2, hist_percent_all, align='center', width=0.4, color="#88CCEE", label='Before accepting')
plt.bar(np.arange(max_cookies + 1) + 0.2, hist_percent_accept, align='center', width=0.4, color="#DDCC77", label='After accepting')
plt.xticks(np.arange(max_cookies + 1))
plt.xlabel('Number of Cookies', fontsize=16)
plt.ylabel('Percentage of Appearance (%)', fontsize=16)
ax = plt.gca()
ax.set_ylim([0, 60])
y_ticks = ax.get_yticks()
for y in y_ticks:
    plt.axhline(y=y, color='#cfcccc', linestyle='--', linewidth=0.3)
plt.axvline(n_mean_all, color='k', linestyle='dashed', linewidth=1, label=f'Mean Before = {round(n_mean_all, 2)}')
plt.axvline(n_mean_accept, color='r', linestyle='dashed', linewidth=1, label=f'Mean After = {round(n_mean_accept, 2)}')
plt.text(n_mean_accept + 0.2, 42, r'$\mu_{before}$ = ' + str(round(n_mean_all, 2)), fontsize=14, color='black')
plt.text(n_mean_accept + 0.2, 38, r'$\mu_{after}$ = ' + str(round(n_mean_accept, 2)), fontsize=14, color='red')
plt.legend()
plt.savefig('img_combined_cookies_histogram.pdf', format="PDF", bbox_inches='tight')

# Print the exact percentages for each data label and occurrence
print("Percentages for 'Before accepting':")
for i, percent in enumerate(hist_percent_all):
    print(f"Number of Cookies: {i}, Percentage: {percent:.2f}%")

print("\nPercentages for 'After accepting':")
for i, percent in enumerate(hist_percent_accept):
    print(f"Number of Cookies: {i}, Percentage: {percent:.2f}%")

# Plot combined beacon histogram.
max_beacons = 30
n_mean_all = sum(number_of_beacons_array) / len(number_of_beacons_array)
n_mean_accept = sum(number_of_beacons_accept_array) / len(number_of_beacons_accept_array)
bins = np.arange(max_beacons + 2) - 0.5
hist_all, bins = np.histogram(number_of_beacons_array, bins=bins)
hist_percent_all = (hist_all / len(number_of_beacons_array)) * 100
hist_accept, bins = np.histogram(number_of_beacons_accept_array, bins=bins)
hist_percent_accept = (hist_accept / len(number_of_beacons_accept_array)) * 100
plt.figure(figsize=(10, 6))
plt.bar(np.arange(max_beacons + 1) - 0.2, hist_percent_all, align='center', width=0.4, color="#88CCEE", label='Before accepting')
plt.bar(np.arange(max_beacons + 1) + 0.2, hist_percent_accept, align='center', width=0.4, color="#DDCC77", label='After accepting')
plt.xticks(np.arange(max_beacons + 1))
plt.xlabel('Number of Pixels', fontsize=16)
plt.ylabel('Percentage of Appearance (%)', fontsize=16)
ax = plt.gca()
ax.set_ylim([0, 40])
y_ticks = ax.get_yticks()
for y in y_ticks:
    plt.axhline(y=y, color='#cfcccc', linestyle='--', linewidth=0.3)
plt.axvline(n_mean_all, color='k', linestyle='dashed', linewidth=1, label=f'Mean Before = {round(n_mean_all, 2)}')
plt.axvline(n_mean_accept, color='r', linestyle='dashed', linewidth=1, label=f'Mean After = {round(n_mean_accept, 2)}')
plt.text(n_mean_all + 0.3, 26, r'$\mu_{before}$ = ' + str(round(n_mean_all, 2)), fontsize=14, color='black')
plt.text(n_mean_accept + 0.3, 26, r'$\mu_{after}$ = ' + str(round(n_mean_accept, 2)), fontsize=14, color='red')
plt.legend()
plt.savefig('img_combined_beacons_histogram.pdf', format="PDF", bbox_inches='tight')

# Print the exact percentages for each data label and occurrence
print("Percentages for 'Before accepting':")
for i, percent in enumerate(hist_percent_all):
    print(f"Number of Pixels: {i}, Percentage: {percent:.2f}%")

print("\nPercentages for 'After accepting':")
for i, percent in enumerate(hist_percent_accept):
    print(f"Number of Pixels: {i}, Percentage: {percent:.2f}%")
