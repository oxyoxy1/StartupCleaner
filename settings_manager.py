import json
import os

SETTINGS_FILE = "assets/config.json"
DEFAULT_SETTINGS = {
    "dark_mode": True,
    "logs_enabled": True,
    "backup_location": "backup.json"
}

def load_settings():
    """Load settings from file or return defaults."""
    if not os.path.exists(SETTINGS_FILE):
        save_settings(DEFAULT_SETTINGS)
    try:
        with open(SETTINGS_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading settings: {e}")
        return DEFAULT_SETTINGS

def save_settings(settings):
    """Save settings to the settings file."""
    try:
        with open(SETTINGS_FILE, "w") as f:
            json.dump(settings, f)
        return True
    except Exception as e:
        print(f"Error saving settings: {e}")
        return False
