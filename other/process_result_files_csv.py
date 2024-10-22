import os
import pandas as pd

# Define the paths
folder_path = "./results"  # Replace with the path to your folder
tranco_file = "tranco.csv"  # Replace with the path to your tranco.csv
output_file = "sample.csv"  # Replace with the desired output path for sample.csv

# Get a list of IDs from the folder
ids_in_folder = set()
for filename in os.listdir(folder_path):
    if filename.endswith(".csv"):
        id = filename[:-4]  # Remove the '.csv' extension to get the ID
        ids_in_folder.add(id)

# Read the tranco.csv file
tranco_df = pd.read_csv(tranco_file, header=None)

# Assign column names to the DataFrame
tranco_df.columns = ['id', 'name']

# Filter the tranco_df to include only the rows with IDs present in the folder
filtered_tranco_df = tranco_df[tranco_df['id'].astype(str).isin(ids_in_folder)]

# Write the filtered dataframe to a new CSV file
filtered_tranco_df.to_csv(output_file, index=False)

print(f"Filtered data has been written to {output_file}")