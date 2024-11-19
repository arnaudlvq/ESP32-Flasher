# ESP32 Flasher GUI Application

Welcome to the **ESP32 Flasher GUI Application**—a simple, fast, and user-friendly tool designed for Windows environments to streamline the flashing process of ESP32 devices. This application is perfect for production environments where efficiency and ease of use are paramount.

## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Getting Started](#getting-started)
  - [1. Export Compiled Binaries](#1-export-compiled-binaries)
  - [2. Prepare the `bin` Directory](#2-prepare-the-bin-directory)
  - [3. Install Required Libraries](#3-install-required-libraries)
  - [4. Run the Application](#4-run-the-application)
- [Usage](#usage)
- [Troubleshooting](#troubleshooting)
- [License](#license)

---

## Features

- **User-Friendly GUI**: Intuitive interface built with Tkinter for ease of use.
- **Dynamic Port Detection**: Automatically detects available COM ports in real-time.
- **Customizable Binary Selection**: Allows selection of application, bootloader, and partition binary files.
- **Fast Flashing**: Utilizes high baud rates for quick flashing operations.
- **Production-Ready**: Ideal for environments where multiple devices need to be flashed efficiently.

---

## Prerequisites

- **Operating System**: Windows
- **Python**: Version 3.x installed
- **Arduino IDE**: For compiling and exporting binaries
- **ESP32 Board**: The target device for flashing

---

## Getting Started

Follow these steps to set up and use the ESP32 Flasher GUI Application.

### 1. Export Compiled Binaries

First, you need to generate the necessary binary files from your Arduino project.

1. Open your sketch in the **Arduino IDE**.
2. Navigate to **`Sketch` > `Export Compiled Binary`**.
3. The IDE will compile your sketch and generate binary files, including:
   - `*.ino.bin` (Application Binary)
   - `*.bootloader.bin` (Bootloader Binary)
   - `*.partitions.bin` (Partition Binary)
4. Locate these files in your sketch's project folder.

---

### 2. Prepare the `bin` Directory

1. Create a folder named `bin` at the root of the ESP32 Flasher application directory.
2. Place the following binary files into the `bin` folder:
   - **Application Binary**: `*.ino.bin`
   - **Bootloader Binary**: `*.bootloader.bin`
   - **Partition Binary**: `*.partitions.bin`

---

### 3. Install Required Libraries

Ensure the following Python libraries are installed:

- **Tkinter**: Should be included with Python on Windows.
- **pyserial**: For serial communication.
- **esptool**: For flashing the ESP32.

**Installation Commands**:

```bash
pip install pyserial
pip install esptool
```

### 4. Run the Application

To start using the ESP32 Flasher GUI Application:

1. **Run the Script**:
   - Open a terminal or command prompt.
   - Navigate to the directory where the `esp32_flasher.py` script is located.
   - Run the script using:
     ```bash
     python esp32_flasher.py
     ```
   - Alternatively, you can double-click the `esp32_flasher.py` file to launch it (if your system is configured to run `.py` files with Python).

2. **Launch the GUI**:
   - The graphical interface will open, allowing you to interact with the application.

---

## Usage

1. **Select COM Port**:
   - Use the drop-down menu to select the COM port corresponding to your ESP32 device.
   - The application dynamically updates the list of available ports.

2. **Select Binary Files**:
   - **Application Binary**: Choose the `*.ino.bin` file generated from the Arduino IDE.
   - **Bootloader Binary**: Select the `*.bootloader.bin` file from your `bin` folder.
   - **Partition Binary**: Select the `*.partitions.bin` file from your `bin` folder.

3. **Flash ESP32**:
   - Click the **"Flash ESP32"** button to start the flashing process.
   - When prompted, hold the **BOOT** button on your ESP32 device to put it in bootloader mode.
   - The status will be displayed in the GUI, indicating the progress and success of the operation.

4. **Completion**:
   - Upon successful flashing, a message box will confirm the process is complete.
   - Disconnect and reset your ESP32 to begin using your flashed firmware.

---

## Troubleshooting

- **No COM Ports Detected**:
  - Ensure your ESP32 is connected to your computer via USB.
  - Check the cable and USB port functionality.
  - Verify that the required drivers for your ESP32 device are installed.

- **Binary Files Not Found**:
  - Confirm the `bin` directory is in the application root.
  - Ensure the necessary binary files (`*.ino.bin`, `*.bootloader.bin`, `*.partitions.bin`) are placed correctly in the `bin` directory.

- **Flashing Errors**:
  - Ensure the ESP32 is in bootloader mode by holding the **BOOT** button during the process (Some Dev Boards are automatically switching)
  - Check for any other applications (e.g., serial monitors) using the COM port (Close your Arduino IDE for example !).
  - Verify you have selected the correct files and COM port in the GUI.

---

## Summary

The ESP32 Flasher GUI Application simplifies the flashing process for ESP32 devices by providing:

- A clean and intuitive graphical interface.
- Dynamic COM port and file selection.
- Fast and reliable flashing for production environments.

With just a few clicks, you can flash your ESP32 device with the required binaries and start running your custom firmware immediately.
