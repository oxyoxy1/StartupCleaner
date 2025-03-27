import tkinter as tk
from tkinter import messagebox
import winreg as reg
import csv
import os

def get_full_startup_items():
    """Get a comprehensive list of startup items like Task Manager (Enabled + Disabled, User + System, 64/32-bit)"""
    startup_items = []

    registry_paths = [
        # Enabled
        (reg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", "Enabled (User)"),
        (reg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Run", "Enabled (System - 64bit)"),
        (reg.HKEY_LOCAL_MACHINE, r"Software\Wow6432Node\Microsoft\Windows\CurrentVersion\Run", "Enabled (System - 32bit)"),

        # Disabled
        (reg.HKEY_CURRENT_USER, r"Software\Microsoft\Shared Tools\MSConfig\startupfolder", "Disabled (Startup Folder)"),
        (reg.HKEY_CURRENT_USER, r"Software\Microsoft\Shared Tools\MSConfig\startupreg", "Disabled (Registry - User)"),
        (reg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Shared Tools\MSConfig\startupreg", "Disabled (Registry - System)"),
    ]

    for root, path, status in registry_paths:
        try:
            registry_key = reg.OpenKey(root, path)
            i = 0
            while True:
                try:
                    name, value, _ = reg.EnumValue(registry_key, i)
                    startup_items.append((name, value, status))
                    i += 1
                except OSError:
                    break
            reg.CloseKey(registry_key)
        except FileNotFoundError:
            continue
        except Exception as e:
            print(f"Error reading {path}: {e}")

    return startup_items

def enable_registry_item(name):
    try:
        # Get the disabled value
        disabled_key = reg.OpenKey(reg.HKEY_CURRENT_USER, r"Software\Microsoft\Shared Tools\MSConfig\startupfolder", 0, reg.KEY_ALL_ACCESS)
        value, _, _ = reg.QueryValueEx(disabled_key, name)
        # Write to enabled
        enabled_key = reg.OpenKey(reg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, reg.KEY_ALL_ACCESS)
        reg.SetValueEx(enabled_key, name, 0, reg.REG_SZ, value)
        # Delete from disabled
        reg.DeleteValue(disabled_key, name)
        reg.CloseKey(enabled_key)
        reg.CloseKey(disabled_key)
        messagebox.showinfo("Success", f"'{name}' has been enabled.")
    except FileNotFoundError:
        messagebox.showerror("Error", f"'{name}' not found in disabled startup items.")
    except Exception as e:
        messagebox.showerror("Error", f"Error enabling startup item: {e}")

def disable_registry_item(name):
    try:
        # Get the enabled value
        enabled_key = reg.OpenKey(reg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, reg.KEY_ALL_ACCESS)
        value, _, _ = reg.QueryValueEx(enabled_key, name)
        # Write to disabled
        disabled_key = reg.CreateKey(reg.HKEY_CURRENT_USER, r"Software\Microsoft\Shared Tools\MSConfig\startupfolder")
        reg.SetValueEx(disabled_key, name, 0, reg.REG_SZ, value)
        # Delete from enabled
        reg.DeleteValue(enabled_key, name)
        reg.CloseKey(enabled_key)
        reg.CloseKey(disabled_key)
        messagebox.showinfo("Success", f"'{name}' has been disabled.")
    except FileNotFoundError:
        messagebox.showerror("Error", f"'{name}' not found in enabled startup items.")
    except Exception as e:
        messagebox.showerror("Error", f"Error disabling startup item: {e}")

def update_startup_list():
    startup_listbox.delete(0, tk.END)
    registry_items = get_full_startup_items()

    # Sort: Enabled first, then Disabled, then Unknown
    registry_items.sort(key=lambda item: (0 if "Enabled" in item[2] else 1 if "Disabled" in item[2] else 2, item[0].lower()))

    for name, value, status in registry_items:
        startup_listbox.insert(tk.END, f"{name} | {status}")

        # Coloring
        if "Enabled" in status:
            startup_listbox.itemconfig(tk.END, {'fg': 'green'})
        elif "Disabled" in status:
            startup_listbox.itemconfig(tk.END, {'fg': 'red'})
        else:
            startup_listbox.itemconfig(tk.END, {'fg': 'gray'})

def on_item_click(event):
    selection = startup_listbox.curselection()
    if not selection:
        return
    index = selection[0]
    item = startup_listbox.get(index)
    
    # Extract name and status
    if " | " not in item:
        messagebox.showerror("Error", "Invalid item format.")
        return

    name, status = item.split(" | ", 1)

    if "Enabled" in status:
        if messagebox.askyesno("Disable", f"Do you want to disable '{name}'?"):
            disable_registry_item(name)
    elif "Disabled" in status:
        if messagebox.askyesno("Enable", f"Do you want to enable '{name}'?"):
            enable_registry_item(name)
    else:
        messagebox.showwarning("Unknown Status", f"Unknown status for '{name}': {status}")

    update_startup_list()

def on_right_click(event):
    try:
        startup_listbox.selection_clear(0, tk.END)
        startup_listbox.selection_set(startup_listbox.nearest(event.y))
        context_menu.tk_popup(event.x_root, event.y_root)
    finally:
        context_menu.grab_release()

def context_action(action):
    selection = startup_listbox.curselection()
    if not selection:
        return
    index = selection[0]
    item = startup_listbox.get(index)
    name, status = item.split(" | ", 1)
    name = name.strip()

    if action == "enable" and "Disabled" in status:
        enable_registry_item(name)
    elif action == "disable" and "Enabled" in status:
        disable_registry_item(name)
    elif action == "details":
        # show registry info
        show_details(name, status)
    else:
        messagebox.showinfo("Info", f"'{name}' is already {status}.")

    update_startup_list()

def show_details(name, status):
    detail_text = f"Name: {name}\nStatus: {status}\n\n(Registry path varies by status)"
    messagebox.showinfo("Details", detail_text)

def on_item_select(event):
    # When the user selects multiple items by holding 'Ctrl' or 'Shift'
    selection = startup_listbox.curselection()
    selected_items = [startup_listbox.get(i) for i in selection]

    if not selected_items:
        return

    action = "Enable" if "(Disabled)" in selected_items[0] else "Disable"

    if messagebox.askyesno(action, f"Do you want to {action.lower()} {len(selected_items)} items?"):
        for item in selected_items:
            name, status = item.split(" | ", 1)
            name = name.strip()

            if action == "Enable" and "Disabled" in status:
                enable_registry_item(name)
            elif action == "Disable" and "Enabled" in status:
                disable_registry_item(name)

        update_startup_list()

def add_startup_item():
    def save_item():
        name = name_entry.get()
        path = path_entry.get()
        if name and path:
            try:
                enabled_key = reg.OpenKey(reg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, reg.KEY_ALL_ACCESS)
                reg.SetValueEx(enabled_key, name, 0, reg.REG_SZ, path)
                reg.CloseKey(enabled_key)
                messagebox.showinfo("Success", f"'{name}' added to startup.")
                update_startup_list()
                add_window.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Error adding startup item: {e}")

    add_window = tk.Toplevel(root)
    add_window.title("Add Startup Item")

    tk.Label(add_window, text="Name:").pack(padx=10, pady=5)
    name_entry = tk.Entry(add_window)
    name_entry.pack(padx=10, pady=5)

    tk.Label(add_window, text="Path:").pack(padx=10, pady=5)
    path_entry = tk.Entry(add_window)
    path_entry.pack(padx=10, pady=5)

    tk.Button(add_window, text="Save", command=save_item).pack(pady=10)
    tk.Button(add_window, text="Cancel", command=add_window.destroy).pack(pady=5)

def export_startup_list():
    try:
        # Ensure the 'exports' folder exists
        exports_folder = "exports"
        if not os.path.exists(exports_folder):
            os.makedirs(exports_folder)  # Create the folder if it doesn't exist

        # Path to the CSV file inside the 'exports' folder
        file_path = os.path.join(exports_folder, "startup_items.csv")

        # Open the file for writing
        with open(file_path, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Name", "Path", "Status"])

            for item in startup_listbox.get(0, tk.END):
                parts = item.split(" | ")
                
                # Ensure the item has at least name and status
                if len(parts) >= 2:
                    name = parts[0].strip()
                    status = parts[1].strip()

                    # If path is missing, leave it as an empty string
                    path = ""  # Modify as needed if you want to gather path information

                    # Write the row to the CSV file
                    writer.writerow([name, path, status])
                else:
                    print(f"Skipping invalid item: {item}")

        # Notify user on success
        messagebox.showinfo("Success", f"Startup items exported to {file_path}")

    except Exception as e:
        messagebox.showerror("Error", f"Error exporting to CSV: {e}")

def is_critical_system_item(name):
    critical_items = [
        "Defender", "Windows Defender", "nvtray", "spoolsv", "explorer", "svchost"
    ]
    return any(critical_item in name for critical_item in critical_items)

def context_action(action):
    selection = startup_listbox.curselection()
    if not selection:
        return
    index = selection[0]
    item = startup_listbox.get(index)
    name, status = item.split(" | ", 1)
    name = name.strip()

    if is_critical_system_item(name):
        messagebox.showwarning("Warning", f"'{name}' is a critical system item. Action may be restricted.")
        return

    if action == "enable" and "Disabled" in status:
        enable_registry_item(name)
    elif action == "disable" and "Enabled" in status:
        disable_registry_item(name)
    elif action == "details":
        show_details(name, status)
    else:
        messagebox.showinfo("Info", f"'{name}' is already {status}.")

    update_startup_list()

def auto_refresh():
    update_startup_list()
    root.after(60000, auto_refresh)  # Refresh every 60 seconds

def show_command_line(name):
    try:
        reg_key = reg.OpenKey(reg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, reg.KEY_READ)
        value, _, _ = reg.QueryValueEx(reg_key, name)
        command_line = value.strip()
        reg.CloseKey(reg_key)

        messagebox.showinfo("Command Line", f"Command line for '{name}': {command_line}")
    except Exception as e:
        messagebox.showerror("Error", f"Error retrieving command line: {e}")

# GUI
root = tk.Tk()
root.title("Startup Item Manager")

root.resizable(True, True)  # resizing
root.geometry("400x500")  # fixed size

startup_listbox = tk.Listbox(root, width=60, height=20)
startup_listbox.grid(row=0, column=0, columnspan=4, padx=10, pady=10)
startup_listbox.bind("<Double-Button-1>", on_item_click)
startup_listbox.bind("<Button-3>", on_right_click)
startup_listbox.bind("<Control-Button-1>", on_item_select)  # Ctrl + Click
startup_listbox.bind("<Shift-Button-1>", on_item_select)  # Shift + Click

context_menu = tk.Menu(root, tearoff=0)
context_menu.add_command(label="Enable", command=lambda: context_action("enable"))
context_menu.add_command(label="Disable", command=lambda: context_action("disable"))
context_menu.add_separator()
context_menu.add_command(label="Details", command=lambda: context_action("details"))

# Add buttons with grid layout
update_button = tk.Button(root, text="Refresh", command=update_startup_list)
update_button.grid(row=1, column=0, padx=10, pady=5)

add_button = tk.Button(root, text="Add Startup Item", command=add_startup_item)
add_button.grid(row=2, column=0, padx=10, pady=5)

export_button = tk.Button(root, text="Export to CSV", command=export_startup_list)
export_button.grid(row=3, column=0, padx=10, pady=5)

auto_refresh_button = tk.Button(root, text="Auto-Refresh (1 min)", command=auto_refresh)
auto_refresh_button.grid(row=4, column=0, padx=10, pady=5)

update_startup_list()
root.mainloop()
