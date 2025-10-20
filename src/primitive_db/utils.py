import json
import os

from .decorators import handle_db_errors

DATA_DIR = 'data'


def ensure_data_dir():
    """
    Ensure data directory exists.
    """
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)


@handle_db_errors
def load_table_data(table_name):
    """
    Load table data from JSON. Return empty list if not found.
    """
    ensure_data_dir()
    filepath = os.path.join(DATA_DIR, f'{table_name}.json')
    if not os.path.exists(filepath):
        return []
    with open(filepath, 'r') as f:
        return json.load(f)


@handle_db_errors
def save_table_data(table_name, data):
    """
    Save table data to JSON.
    """
    ensure_data_dir()
    filepath = os.path.join(DATA_DIR, f'{table_name}.json')
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=4)


@handle_db_errors
def load_metadata(filepath):
    """
    Load metadata from JSON file. Return empty dict if file not found.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError
    with open(filepath, 'r') as f:
        return json.load(f)


@handle_db_errors
def save_metadata(filepath, data):
    """
    Save data to JSON file.
    """
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=4)
