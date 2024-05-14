import pandas as pd
import os

# Path to the large CSV file
input_csv_path = 'output.csv'

# Directory to store the smaller CSV files
output_dir = 'output_directory'

# Number of rows per smaller CSV file
rows_per_file = 5000  # Adjust this value as needed

# Create the output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

# Read the large CSV file in chunks
chunk_size = rows_per_file
chunk_number = 1

for chunk in pd.read_csv(input_csv_path, chunksize=chunk_size):
    output_csv_path = os.path.join(output_dir, f'output_{chunk_number}.csv')
    chunk.to_csv(output_csv_path, index=False)
    print(f'Saved {output_csv_path}')
    chunk_number += 1
