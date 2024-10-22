import os
import random
import pandas as pd

# Define the folder path
folder_path = "./results"  # Replace with the path to your folder
tranco_file = "tranco.csv"  # Replace with the path to your tranco.csv
output_file = "random_sample.csv"  # Replace with the desired output path for random_sample.csv

# Get a list of IDs from the CSV files in the folder
ids_in_folder = [filename[:-4] for filename in os.listdir(folder_path) if filename.endswith('.csv')]

# Check if there are enough IDs
if len(ids_in_folder) < 100:
    raise ValueError("There are fewer than 100 IDs in the specified folder.")

# Read the tranco.csv file
tranco_df = pd.read_csv(tranco_file, header=None)

# Assign column names to the DataFrame
tranco_df.columns = ['id', 'name']

# Filter tranco_df to only include rows with IDs in ids_in_folder
filtered_tranco_df = tranco_df[tranco_df["id"].astype(str).isin(ids_in_folder)]

# Check if there are enough rows after filtering
if len(filtered_tranco_df) < 100:
    raise ValueError("There are fewer than 100 matching IDs in the tranco.csv file.")

# Randomly select 100 rows from the filtered DataFrame
random_sample_df = filtered_tranco_df.sample(n=100)

# Write the random sample DataFrame to a new CSV file
random_sample_df.to_csv(output_file, index=False)

print(f"Random sample of 100 IDs and names has been written to {output_file}")