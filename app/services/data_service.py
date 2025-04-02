import os
import json
import threading
from typing import List, Dict, Optional, Any
from flask import current_app

# Simple file-based locking mechanism
# In a real-world scenario with high concurrency, a more robust locking mechanism (e.g., filelock library) would be better.
_locks = {}
_lock_lock = threading.Lock()

def _get_file_lock(file_path: str) -> threading.Lock:
    """Returns a lock specific to a file path."""
    with _lock_lock:
        if file_path not in _locks:
            _locks[file_path] = threading.Lock()
        return _locks[file_path]

def _get_file_path(file_name: str) -> str:
    """Constructs the full path to the data file."""
    # Ensure file_name ends with .json
    if not file_name.endswith('.json'):
        file_name += '.json'
    return os.path.join(current_app.config['DATA_DIR'], file_name)

def read_data(file_name: str) -> List[Dict[str, Any]]:
    """Reads all data from a JSON file."""
    file_path = _get_file_path(file_name)
    lock = _get_file_lock(file_path)
    with lock:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if not isinstance(data, list):
                    current_app.logger.error(f"Data in {file_name} is not a list. Reinitializing.")
                    return []
                return data
        except FileNotFoundError:
            # If file doesn't exist, return empty list (and create it on first write)
            return []
        except json.JSONDecodeError:
            # If file is empty or corrupt, return empty list
            current_app.logger.error(f"Error decoding JSON from {file_name}. Returning empty list.")
            return []

def write_data(file_name: str, data: List[Dict[str, Any]]) -> None:
    """Writes data to a JSON file, overwriting existing content."""
    file_path = _get_file_path(file_name)
    lock = _get_file_lock(file_path)
    with lock:
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except IOError as e:
            current_app.logger.error(f"Error writing to {file_name}: {e}")
            # Optionally raise an exception or handle it differently
            raise

def get_next_id(file_name: str) -> int:
    """Generates the next unique ID for a record in a file."""
    data = read_data(file_name)
    if not data:
        return 1
    # Find the maximum current ID and add 1
    max_id = max(item.get('id', 0) for item in data)
    return max_id + 1

def find_one(file_name: str, **kwargs) -> Optional[Dict[str, Any]]:
    """Finds the first item matching the given criteria."""
    data = read_data(file_name)
    for item in data:
        if all(item.get(key) == value for key, value in kwargs.items()):
            return item
    return None

def find_many(file_name: str, **kwargs) -> List[Dict[str, Any]]:
    """Finds all items matching the given criteria."""
    data = read_data(file_name)
    results = []
    for item in data:
        if all(item.get(key) == value for key, value in kwargs.items()):
            results.append(item)
    return results

def add_item(file_name: str, item: Dict[str, Any], assign_id: bool = True) -> Dict[str, Any]:
    """Adds a new item to the data file, assigning a new ID if requested."""
    data = read_data(file_name)
    if assign_id:
        if 'id' in item and item['id'] is not None:
            # Check for ID collision if ID is pre-assigned
            if any(existing_item.get('id') == item['id'] for existing_item in data):
                raise ValueError(f"Item with ID {item['id']} already exists in {file_name}")
        else:
            item['id'] = get_next_id(file_name)

    elif 'id' not in item or item['id'] is None:
         raise ValueError(f"Item must have an ID if assign_id is False in {file_name}")
    elif any(existing_item.get('id') == item['id'] for existing_item in data):
         raise ValueError(f"Item with ID {item['id']} already exists in {file_name}")


    data.append(item)
    write_data(file_name, data)
    return item

def update_item(file_name: str, item_id: int, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Updates an existing item identified by its ID."""
    data = read_data(file_name)
    updated = False
    for i, item in enumerate(data):
        if item.get('id') == item_id:
            # Prevent changing the ID via update
            updates.pop('id', None)
            item.update(updates)
            data[i] = item
            updated = True
            break

    if updated:
        write_data(file_name, data)
        return data[i] # Return the updated item
    return None # Item not found

def delete_item(file_name: str, item_id: int) -> bool:
    """Deletes an item identified by its ID."""
    data = read_data(file_name)
    initial_length = len(data)
    # Filter out the item to be deleted
    new_data = [item for item in data if item.get('id') != item_id]

    if len(new_data) < initial_length:
        write_data(file_name, new_data)
        return True # Deletion successful
    return False # Item not found

def delete_many(file_name: str, **kwargs) -> int:
    """Deletes all items matching the given criteria."""
    data = read_data(file_name)
    initial_length = len(data)
    # Keep items that *don't* match all criteria
    new_data = [
        item for item in data
        if not all(item.get(key) == value for key, value in kwargs.items())
    ]

    if len(new_data) < initial_length:
        write_data(file_name, new_data)
        return initial_length - len(new_data) # Return number of deleted items
    return 0 # No items matched 