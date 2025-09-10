# Easy Production Proof ESP32 Flasher (PySide6 & Tkinter) + MacOS APP

A simple, user-friendly GUI application for flashing ESP32 microcontrollers on macOS, Windows, and Linux.

This repository provides two versions of the flasher:
- **`flasher.py`**: A feature-rich version using **PySide6**, which is used to build the standalone macOS `.app`.
- **`flasher_tk.py`**: A lightweight version using **Tkinter**, ideal for running directly with Python without extra dependencies. (If your python compiled version include Tkinter)

### PySide6 Version (Recommended for macOS App)
<img width="818" height="627" alt="PySide6 Flasher" src="https://github.com/user-attachments/assets/fca886f6-0e7b-4979-99a2-bb23a972967f" />

### Tkinter Version (Lightweight)
![Tkinter Flasher](https://github.com/user-attachments/assets/e6e47eca-333e-478f-a35c-4a3165678c2a)

## Table of Contents

- [Installation](#installation)
  - [1. Using the Pre-built macOS App](#1-using-the-pre-built-macos-app)
  - [2. Running from Source (All Platforms)](#2-running-from-source-all-platforms)
- [Getting Your Binary Files](#getting-your-binary-files)
- [Usage](#usage)
- [For Developers](#for-developers)
  - [Customizing the Flash Configuration](#customizing-the-flash-configuration)
  - [Building the macOS Application](#building-the-macos-application)
- [Troubleshooting](#troubleshooting)
- [License](#license)

---

## Installation

You have two options for using the flasher: using the pre-built macOS application or running the Python script from source.

### 1. Running from Source (All Platforms)

This method works on Windows, macOS, and Linux, but requires Python to be installed.

#### Prerequisites

- **Python 3**
- **Required Libraries**:
  - For the **PySide6 version** (`flasher.py`):
    ```bash
    pip install esptool pyside6 pyserial
    ```
  - For the **Tkinter version** (`flasher_tk.py`):
    ```bash
    pip install esptool pyserial
    ```
    *(Tkinter is usually included with standard Python installations).*

#### How to Run

1.  Open your terminal or command prompt.
2.  Navigate to the project directory.
3.  Create a `bin` folder in the root of the project and place your firmware files inside.
4.  Run your desired version:
    - **PySide6 version**: `python flasher.py`
    - **Tkinter version**: `python flasher_tk.py`


### 2. Using the Pre-built macOS App

This is the easiest method for macOS users. **No Python installation is required.**
disclaimer : this is compiled for esp32c3 with OTA partitionning. The re-compilation steps for other esp chips are easy and described bellow.

1.  Download the latest release or look inside the `macOS_app_build/build/Flasher` folder.
2.  You will find the `Flasher.app`. You can move this application to your `Applications` folder or anywhere you like.
3.  **Before launching the app**, create a folder named `bin` in the **same directory** as `Flasher.app`.
4.  Place your firmware binary files inside the `bin` folder (see [Getting Your Binary Files](#getting-your-binary-files)).
5.  Double-click `Flasher.app` to run it.


---

## Getting Your Binary Files

A "successful" flash only means that data has been written to the chip's memory. For the device to boot correctly, you must use the correct binary files at the correct memory addresses.

The most reliable way to get these is from the **Arduino IDE**.

1.  **Enable Verbose Output**:
    - In the Arduino IDE, go to `File > Preferences`.
    - Check the box for `Show verbose output during: [x] upload`.

2.  **Upload Your Sketch**:
    - Connect your board and upload your sketch as you normally would.

3.  **Analyze the Output**:
    - In the console, find the `esptool.py` command. It will look like this:
    ```
    esptool.py --chip esp32c3 --port "/dev/cu.usbserial-0001" --baud 921600 write_flash -z 0x0 /path/to/your/bootloader.bin 0x8000 /path/to/your/partitions.bin 0xe000 /path/to/boot_app0.bin 0x10000 /path/to/your/application.ino.bin
    ```

4.  **Gather the Files**:
    - The command gives you the exact paths to the essential files. Copy these files into this project's `bin` directory:
        - `bootloader.bin`
        - `partitions.bin`
        - `boot_app0.bin` (Crucial for OTA-enabled partitions, tells the ESP32 which partition to boot first).
        - `your_sketch.ino.bin` (your compiled application).

---

## Usage

1.  **Launch the Application**: Either by opening `Flasher.app` or running `python flasher.py` / `python flasher_tk.py`.
2.  **Select COM Port**: The application will automatically detect and list available serial ports. Choose the one corresponding to your ESP32.
3.  **Select Binary Files** (Tkinter version only): The Tkinter GUI allows you to manually select your binary files. The PySide6 version automatically uses the files from the `bin` folder.
4.  **Flash ESP32**: Click the **"Flash ESP32"** button.
5.  **Enter Bootloader Mode**: If prompted, hold the **BOOT** button on your ESP32, press and release the **EN** (or RST) button, and then release **BOOT**. *Note: Many modern ESP32 boards handle this automatically.*
6.  **Monitor Progress**: The application will display the flashing status. A confirmation message will appear upon completion.

---

## For Developers

### Customizing the Flash Configuration

If you need to support a different ESP32 chip (e.g., `esp32s3`), change firmware addresses, or modify the flashing logic, you can edit `flasher.py`.

1.  Open `flasher.py` in a code editor.
2.  Locate the `flash_firmware` method.
3.  Modify the `esptool_args` list to fit your needs.

    ```python
    # Example from the code
    esptool_args = [
        'esptool',
        '--chip', 'esp32c3',  # <-- Change chip here
        '--port', self.port_selector.currentText(),
        '--baud', '921600',
        'write_flash',
        # Addresses and file paths
        '0x0', os.path.join(BIN_DIR, 'bootloader.bin'),
        '0x8000', os.path.join(BIN_DIR, 'partition-table.bin'),
        '0xe000', os.path.join(BIN_DIR, 'boot_app0.bin'),
        '0x10000', os.path.join(BIN_DIR, 'firmware.bin'),
    ]
    ```

### Building the macOS Application

To create a new standalone `Flasher.app` after making changes:

1.  **Install PyInstaller**:
    ```bash
    pip install pyinstaller
    ```
2.  Navigate to the project's root directory.
3.  Run the build command using the provided spec file:
    ```bash
    pyinstaller macOS_app_build/Flasher.spec
    ```
4.  The newly built `Flasher.app` will be in the `dist` folder.

---

## Troubleshooting

-   **No COM Ports Detected**:
    -   Ensure your ESP32 is properly connected to your computer.
    -   Try a different USB cable (some are charger only) and port.
    -   Verify that the necessary drivers (CP210x) for your ESP32 are installed !!

-   **Flashing Errors**:
    -   Make sure the ESP32 is in bootloader mode. (RST + BOOT)
    -   Close any other applications that might be using the COM port (e.g., Arduino IDE's Serial Monitor).
    -   Double-check that you have the correct binary files in the `bin` folder.

-   **Device Not Working After Flash**:
    -   This is almost always due to incorrect binary files or memory addresses.
    -   Carefully follow the steps in the [Getting Your Binary Files](#getting-your-binary-files) section to ensure you have the right files and addresses for your specific board and partition scheme.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
