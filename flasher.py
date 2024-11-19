import tkinter as tk
from tkinter import ttk, messagebox
import serial.tools.list_ports
import threading
import esptool
import os
import time

BIN_DIR = 'bin'  # Directory where the binary files are located

class ESPFlasherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ESP32 Flasher")

        self.create_widgets()
        self.refresh_ports()
        self.refresh_bins()

        # Start a thread to update COM ports dynamically
        threading.Thread(target=self.dynamic_port_update, daemon=True).start()

    def create_widgets(self):
        # Frame for COM port selection
        port_frame = ttk.Frame(self.root)
        port_frame.pack(pady=10)

        port_label = ttk.Label(port_frame, text="Select COM Port:")
        port_label.pack(side=tk.LEFT, padx=5)

        self.port_combo = ttk.Combobox(port_frame, values=[], state="readonly", width=30)
        self.port_combo.pack(side=tk.LEFT)

        # Frame for binary file selection
        bin_frame = ttk.Frame(self.root)
        bin_frame.pack(pady=10)

        bin_label = ttk.Label(bin_frame, text="Select Binary File:")
        bin_label.pack(side=tk.LEFT, padx=5)

        self.bin_combo = ttk.Combobox(bin_frame, values=[], state="readonly", width=30)
        self.bin_combo.pack(side=tk.LEFT)

        # Flash button
        flash_button = ttk.Button(self.root, text="Flash ESP32", command=self.flash_esp32)
        flash_button.pack(pady=20)

        # Status label
        self.status_label = ttk.Label(self.root, text="")
        self.status_label.pack(pady=5)

    def refresh_ports(self):
        ports = serial.tools.list_ports.comports()
        port_list = [f"{port.device} - {port.description}" for port in ports]
        current_selection = self.port_combo.get()
        self.port_combo['values'] = port_list
        if current_selection in port_list:
            self.port_combo.set(current_selection)
        elif port_list:
            self.port_combo.current(0)
        else:
            self.port_combo.set('')

    def refresh_bins(self):
        if not os.path.exists(BIN_DIR):
            os.makedirs(BIN_DIR)
        bin_files = [f for f in os.listdir(BIN_DIR) if f.endswith('.bin')]
        current_selection = self.bin_combo.get()
        self.bin_combo['values'] = bin_files
        if current_selection in bin_files:
            self.bin_combo.set(current_selection)
        elif bin_files:
            self.bin_combo.current(0)
        else:
            self.bin_combo.set('')

    def dynamic_port_update(self):
        previous_ports = set()
        while True:
            ports = set(serial.tools.list_ports.comports())
            if ports != previous_ports:
                self.root.after(0, self.refresh_ports)
                previous_ports = ports
            time.sleep(1)

    def flash_esp32(self):
        selected_port_desc = self.port_combo.get()
        selected_bin = self.bin_combo.get()

        if not selected_port_desc:
            messagebox.showerror("Error", "Please select a COM port.")
            return

        if not selected_bin:
            messagebox.showerror("Error", "Please select a binary file.")
            return

        selected_port = selected_port_desc.split(' - ')[0]
        bin_path = os.path.join(BIN_DIR, selected_bin)

        # Start flashing in a separate thread to prevent GUI freezing
        threading.Thread(target=self.run_esptool, args=(selected_port, bin_path), daemon=True).start()

    def run_esptool(self, port, bin_file):
        try:
            self.update_status("Please hold the BOOT button on your ESP32...")
            time.sleep(2)  # Short delay to allow user to press the BOOT button

            # esptool command
            bootloader_file = bin_file.replace(".bin", ".bootloader.bin")
            partitions_file = bin_file.replace(".bin", ".partitions.bin")
            application_file = bin_file

            esptool_args = [
                '--chip', 'esp32',
                '--port', port,
                '--baud', '460800',
                '--before', 'default_reset',
                '--after', 'hard_reset',
                'write_flash', '-z',
                '0x1000', bootloader_file,
                '0x8000', partitions_file,
                '0x10000', application_file
            ]

            esptool.main(esptool_args)

            self.update_status("Flashing completed successfully!")
            messagebox.showinfo("Success", "Flashing completed successfully!")

        except Exception as e:
            self.update_status("An error occurred.")
            messagebox.showerror("Error", f"An error occurred:\n{str(e)}")

        finally:
            self.refresh_ports()
            self.refresh_bins()

    def update_status(self, message):
        self.status_label.config(text=message)

if __name__ == "__main__":
    root = tk.Tk()
    app = ESPFlasherApp(root)
    root.mainloop()
