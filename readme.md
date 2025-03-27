# Startup Manager

A simple Python application that allows users to manage startup items on their system. You can view, enable/disable, and export the list of startup items. The app provides an easy-to-use interface with a list of current startup entries, their paths, and statuses.

## Features

- View a list of system startup items.
- Enable or disable startup items with a simple toggle.
- Export the list of startup items to a CSV file.
- All items are displayed with their name, path, and status (enabled/disabled).

### Required Libraries:
- `tkinter` for GUI creation
- `psutil` for managing and retrieving system startup items.
- `winreg` (Windows only) for accessing the registry to get startup information.

## Installation

1. Clone the repository or download the files.
   
2. Install dependencies:

    ```
    pip install -r requirements.txt
    ```

3. Run the application:

    ```
    main app.py
    ```

## Usage

- **Viewing Startup Items:** Once you run the program, the list of startup items will be displayed.
- **Enabling/Disabling Items:** You can toggle the status of each item by clicking the buttons next to them.
- **Exporting to CSV:** You can export the current list of startup items to a CSV file by clicking the "Export" button.

## Export Location

The exported CSV file will be saved in the `exports` folder inside your project directory.

## Contributing

If you'd like to contribute, feel free to fork the repository, make changes, and create a pull request.

## License

This project is licensed under the MIT License.
