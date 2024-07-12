import os

import duckdb
import toml

config_file_path = './config.toml'

def set_env_vars(config_file_path: str):
    config = toml.load(config_file_path)
    motherduck_token = config['tokens']['motherduck']
    os.environ['MOTHERDUCK_TOKEN'] = motherduck_token
    motherduck_token_from_env = os.getenv('MOTHERDUCK_TOKEN')

    return motherduck_token_from_env

set_env_vars(config_file_path)

import os

# Load the MotherDuck token from environment variables
motherduck_token = os.getenv('MOTHERDUCK_TOKEN')
if not motherduck_token:
    raise ValueError("MOTHERDUCK_TOKEN is not set in the environment variables.")

# Configuration
conn = duckdb.connect(f'md:demo_cdm?motherduck_token={motherduck_token}')

input_directory = '../demo_cdm'


# Function to load parquet files and create tables in DuckDB
def load_parquet_to_duckdb(input_directory):
    for file_name in os.listdir(input_directory):
        if file_name.endswith('.parquet'):
            table_name = os.path.splitext(file_name)[0]
            file_path = f'{file_name}'


            # Convert PyArrow Table to DuckDB table and save it
            conn.execute(f"""
                         DROP TABLE IF EXISTS {table_name};
                         CREATE TABLE {table_name} AS SELECT * FROM {file_path};
                         """)
            print(f"Table {table_name} created from {file_name}")

# Load all parquet files in the input directory into DuckDB
load_parquet_to_duckdb(input_directory)

# Close the DuckDB connection
conn.close()

print("All parquet files have been loaded into the MotherDuck database.")