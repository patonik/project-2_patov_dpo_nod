import json
import os


def load_metadata(filepath):
    """
    Load metadata from JSON file. Return empty dict if file not found.
    """
    if not os.path.exists(filepath):
        return {}
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def save_metadata(filepath, data):
    """
    Save data to JSON file.
    """
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=4)
