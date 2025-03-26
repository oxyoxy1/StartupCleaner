import json
import os

def backup_startup_items(items, backup_file="backups/backup.json"):
    """Backup the list of startup items with their state to a JSON file."""
    try:
        # Each item is a tuple (name, path, state)
        with open(backup_file, "w") as f:
            json.dump(items, f)
        return True
    except Exception as e:
        print(f"Error backing up items: {e}")
        return False

def restore_startup_items(backup_file="backups/backup.json"):
    """Restore startup items from a JSON backup file, including their state."""
    if not os.path.exists(backup_file):
        print("Backup file does not exist.")
        return []
    try:
        with open(backup_file, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error restoring items: {e}")
        return []