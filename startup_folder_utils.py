import os
import shutil
import winreg

def get_startup_folder():
    """Get a list of files in the startup folder, including active and inactive items."""
    # Path for the active startup folder
    startup_folder = os.path.join(os.getenv("APPDATA"), "Microsoft\\Windows\\Start Menu\\Programs\\Startup")
    
    # List of active items (files in the startup folder)
    active_items = [f for f in os.listdir(startup_folder) if os.path.isfile(os.path.join(startup_folder, f))]
    
    # Registry path for the AutorunsDisabled (disabled items)
    disabled_registry_path = r"Microsoft\\Windows\\CurrentVersion\\Run\\AutorunsDisabled"
    
    # List of disabled items fetched from the registry
    disabled_items = []
    try:
        # Accessing the registry to get the list of disabled startup items
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, disabled_registry_path) as key:
            i = 0
            while True:
                try:
                    # Enumerate all disabled items in the registry
                    disabled_items.append(winreg.EnumValue(key, i)[0])
                    i += 1
                except OSError:
                    break
    except FileNotFoundError:
        # If the registry key doesn't exist, we return an empty list
        pass

    # Debugging: Log the fetched items
    print(f"Active items from Startup folder: {active_items}")
    print(f"Disabled items from Registry: {disabled_items}")
    
    # Combine the active items (from the folder) and the disabled items (from the registry)
    return active_items + disabled_items

def delete_startup_file(file_name):
    """Delete a file from the startup folder."""
    try:
        startup_folder = os.path.join(os.getenv("APPDATA"), "Microsoft\\Windows\\Start Menu\\Programs\\Startup")
        file_path = os.path.join(startup_folder, file_name)
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
    except Exception as e:
        print(f"Error deleting startup file: {e}")
    return False

def enable_startup_file(file_name, file_path):
    """Add a file to the startup folder."""
    try:
        startup_folder = os.path.join(os.getenv("APPDATA"), "Microsoft\\Windows\\Start Menu\\Programs\\Startup")
        shutil.copy(file_path, startup_folder)
        return True
    except Exception as e:
        print(f"Error enabling startup file: {e}")
    return False

# Function to disable a startup file (remove it from execution but don't delete the file)
def disable_startup_file(file_name):
    # Here, we can simply modify the file's permissions or move it out of the startup folder temporarily
    startup_folder = os.path.join(os.getenv("APPDATA"), "Microsoft\\Windows\\Start Menu\\Programs\\Startup")
    file_path = os.path.join(startup_folder, file_name)
    
    # Move the file to a disabled folder (not deleting it, just disabling it)
    disabled_folder = os.path.join(os.getenv("APPDATA"), "Microsoft\\Windows\\Start Menu\\Programs\\Startup\\Disabled")
    
    if not os.path.exists(disabled_folder):
        os.makedirs(disabled_folder)
    
    try:
        shutil.move(file_path, os.path.join(disabled_folder, file_name))
        return True
    except Exception as e:
        print(f"Error disabling startup file: {e}")
    return False