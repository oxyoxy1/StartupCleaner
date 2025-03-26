import winreg as reg
import os

def get_registry_startup():
    """Get a list of startup items from the Windows registry."""
    startup_items = []
    try:
        registry_key = reg.OpenKey(reg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run")
        i = 0
        while True:
            try:
                name, value, _ = reg.EnumValue(registry_key, i)
                startup_items.append((name, value))
                i += 1
            except OSError:
                break
        reg.CloseKey(registry_key)
    except Exception as e:
        print(f"Error reading registry: {e}")
    return startup_items

def delete_registry_item(item_name):
    """Delete a startup item from the registry."""
    try:
        registry_key = reg.OpenKey(reg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, reg.KEY_WRITE)
        reg.DeleteValue(registry_key, item_name)
        reg.CloseKey(registry_key)
        return True
    except Exception as e:
        print(f"Error deleting registry item: {e}")
        return False

def enable_registry_item(item_name, path):
    """Enable a startup item by adding it to the registry."""
    try:
        registry_key = reg.OpenKey(reg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, reg.KEY_WRITE)
        reg.SetValueEx(registry_key, item_name, 0, reg.REG_SZ, path)
        reg.CloseKey(registry_key)
        return True
    except Exception as e:
        print(f"Error enabling registry item: {e}")
        return False

def disable_registry_item(item_name):
    """Disable a startup item by deleting it from the registry."""
    return delete_registry_item(item_name)
