# gui.py
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox, filedialog, scrolledtext
import os
from registry_utils import get_registry_startup, delete_registry_item, enable_registry_item, disable_registry_item
from startup_folder_utils import get_startup_folder, delete_startup_file, enable_startup_file, disable_startup_file
from backup_utils import backup_startup_items, restore_startup_items
from settings_manager import load_settings, save_settings
from logger import log_action

# Load settings (dark mode, logs enabled)
settings = load_settings()

# Function to set dark or light mode
def set_theme():
    if settings["dark_mode"]:
        root.tk_setPalette(background='#2E2E2E', foreground='#FFFFFF')
    else:
        root.tk_setPalette(background='#FFFFFF', foreground='#000000')

# Function to toggle dark mode
def toggle_dark_mode():
    settings["dark_mode"] = dark_mode_var.get()
    save_settings(settings)
    set_theme()  # Reapply the theme based on the new setting

# Function to toggle logs
def toggle_logs():
    settings["logs_enabled"] = logs_var.get()
    save_settings(settings)

# Function to update startup list with status (Enabled/Disabled)
def update_startup_list():
    registry_items = get_registry_startup()
    folder_items = get_startup_folder()

    all_items = registry_items + folder_items

    startup_listbox.delete(0, tk.END)
    
    for item in all_items:
        item_name = item[0] if isinstance(item, tuple) else item
        
        # Check the status of the item
        status = "Enabled" if is_item_enabled(item_name) else "Disabled"
        
        # Debugging: Log the items being added to the list
        print(f"Adding item: {item_name} ({status})")
        
        # Insert into the Listbox
        startup_listbox.insert(tk.END, f"{item_name} ({status})")

# Function to check if a startup item is enabled
def is_item_enabled(item_name):
    # Check if it's in the registry or the startup folder
    registry_items = get_registry_startup()
    folder_items = get_startup_folder()
    
    # Look for the item in both places and check its status
    for item in registry_items:
        if item[0] == item_name:
            return True
    for item in folder_items:
        if item == item_name:
            return True
    return False

# Function to enable a startup item
def enable_startup():
    selected_item = startup_listbox.curselection()
    if selected_item:
        item_name = startup_listbox.get(selected_item).split(" (")[0]  # Get item name without the status
        if item_name in [x[0] for x in get_registry_startup()]:
            enable_registry_item(item_name, item_name)
        else:
            enable_startup_file(item_name, os.path.join(os.getenv("APPDATA"), "Microsoft\\Windows\\Start Menu\\Programs\\Startup", item_name))
        log_action(f"Enabled {item_name}")
        update_startup_list()

# Function to disable a startup item (now marks it as disabled instead of deleting it)
def disable_startup():
    selected_item = startup_listbox.curselection()
    if selected_item:
        item_name = startup_listbox.get(selected_item).split(" (")[0]  # Get item name without the status
        if item_name in [x[0] for x in get_registry_startup()]:
            disable_registry_item(item_name)  # This keeps the registry entry but disables the item
        else:
            # Now call disable_startup_file to move the file to a "Disabled" folder instead of deleting it
            disable_startup_file(item_name)
        log_action(f"Disabled {item_name}")
        update_startup_list()  # Update the list to reflect changes

# Function to delete a startup item
def delete_startup():
    selected_item = startup_listbox.curselection()
    if selected_item:
        item_name = startup_listbox.get(selected_item).split(" (")[0]  # Get item name without the status
        if item_name in [x[0] for x in get_registry_startup()]:
            delete_registry_item(item_name)
        else:
            delete_startup_file(item_name)
        log_action(f"Deleted {item_name}")
        update_startup_list()

# Function to backup startup items
def backup_startup():
    items = get_registry_startup() + get_startup_folder()
    backup_startup_items(items)
    log_action("Backup created.")

# Function to restore startup items
def restore_startup():
    items = restore_startup_items()
    if items:
        log_action("Restored from backup.")
        update_startup_list()

# Function to clear logs
def clear_logs():
    logs_text.delete(1.0, tk.END)

# Set up window
root = tk.Tk()
root.title("Startup Cleaner - oxy edition")

# Set initial theme
set_theme()

# Create the notebook (tabs)
notebook = ttk.Notebook(root)
notebook.pack(padx=10, pady=10, fill='both', expand=True)

# Create the 'Startup Items' tab
startup_frame = ttk.Frame(notebook)
notebook.add(startup_frame, text="Startup Items")

# Listbox for startup items
startup_listbox = tk.Listbox(startup_frame, height=10, width=50)
startup_listbox.pack(padx=10, pady=10)

# Buttons for enabling/disabling/deleting startup items
button_frame = ttk.Frame(startup_frame)
button_frame.pack(padx=10, pady=10)

enable_button = ttk.Button(button_frame, text="Enable", command=enable_startup)
enable_button.grid(row=0, column=0, padx=5)

disable_button = ttk.Button(button_frame, text="Disable", command=disable_startup)
disable_button.grid(row=0, column=1, padx=5)

delete_button = ttk.Button(button_frame, text="Delete", command=delete_startup)
delete_button.grid(row=0, column=2, padx=5)

# Create the 'Backup/Restore' tab
backup_frame = ttk.Frame(notebook)
notebook.add(backup_frame, text="Backup/Restore")

# Buttons for backup and restore
backup_button = ttk.Button(backup_frame, text="Backup", command=backup_startup)
backup_button.pack(padx=10, pady=5)

restore_button = ttk.Button(backup_frame, text="Restore", command=restore_startup)
restore_button.pack(padx=10, pady=5)

# Create the 'Settings' tab
settings_frame = ttk.Frame(notebook)
notebook.add(settings_frame, text="Settings")

# Dark mode toggle
dark_mode_var = tk.BooleanVar(value=settings["dark_mode"])
dark_mode_checkbox = ttk.Checkbutton(settings_frame, text="Dark Mode", variable=dark_mode_var, command=toggle_dark_mode)
dark_mode_checkbox.pack(padx=10, pady=5)

# Log toggle
logs_var = tk.BooleanVar(value=settings["logs_enabled"])
logs_checkbox = ttk.Checkbutton(settings_frame, text="Enable Logs", variable=logs_var, command=toggle_logs)
logs_checkbox.pack(padx=10, pady=5)

# Create the 'Logs' tab
logs_frame = ttk.Frame(notebook)
notebook.add(logs_frame, text="Logs")

# Scrollable logs text area
logs_text = scrolledtext.ScrolledText(logs_frame, width=60, height=20, wrap=tk.WORD, state=tk.DISABLED)
logs_text.pack(padx=10, pady=10)

# Clear logs button
clear_logs_button = ttk.Button(logs_frame, text="Clear Logs", command=clear_logs)
clear_logs_button.pack(padx=10, pady=5)

# Call the update_startup_list function after window initialization
update_startup_list()

# Main loop to handle events
root.mainloop()
