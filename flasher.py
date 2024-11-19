import tkinter as tk
from tkinter import ttk, messagebox, filedialog
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
        self.root.geometry("600x400")

        self.create_widgets()
        self.refresh_ports()
        self.refresh_bins()

        # Start a thread to update COM ports dynamically
        threading.Thread(target=self.dynamic_port_update, daemon=True).start()

    def create_widgets(self):
        # Main container frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Port selection frame
        port_frame = ttk.LabelFrame(main_frame, text="Select COM Port", padding="10")
        port_frame.pack(fill=tk.X, pady=10)

        self.port_combo = ttk.Combobox(port_frame, values=[], state="readonly", width=40)
        self.port_combo.pack(side=tk.LEFT, padx=5, expand=True)

        refresh_ports_button = ttk.Button(port_frame, text="Refresh", command=self.refresh_ports)
        refresh_ports_button.pack(side=tk.RIGHT, padx=5)

        # Binary file selection frame
        file_frame = ttk.LabelFrame(main_frame, text="Select Binary Files", padding="10")
        file_frame.pack(fill=tk.BOTH, pady=10)

        self.create_file_selection(file_frame, "Main Binary File:", "bin_combo", "Browse Main Binary")
        self.create_file_selection(file_frame, "Bootloader File:", "bootloader_combo", "Browse Bootloader")
        self.create_file_selection(file_frame, "Partition File:", "partition_combo", "Browse Partition")

        # Flash button and progress bar
        action_frame = ttk.Frame(main_frame, padding="10")
        action_frame.pack(fill=tk.X, pady=10)

        self.flash_button = ttk.Button(action_frame, text="Flash ESP32", command=self.flash_esp32)
        self.flash_button.pack(side=tk.LEFT, expand=True, padx=5)

        self.progress_bar = ttk.Progressbar(action_frame, mode="indeterminate")
        self.progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        # Status label
        self.status_label = ttk.Label(main_frame, text="", relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(fill=tk.X, pady=5)

    def create_file_selection(self, parent_frame, label_text, attr_name, button_text):
        row = ttk.Frame(parent_frame)
        row.pack(fill=tk.X, pady=5)

        label = ttk.Label(row, text=label_text)
        label.pack(side=tk.LEFT, padx=5)

        combobox = ttk.Combobox(row, values=[], state="readonly", width=30)
        combobox.pack(side=tk.LEFT, expand=True)

        browse_button = ttk.Button(row, text=button_text, command=lambda: self.browse_file(attr_name))
        browse_button.pack(side=tk.RIGHT, padx=5)

        setattr(self, attr_name, combobox)

    def browse_file(self, target_combo_attr):
        file_path = filedialog.askopenfilename(filetypes=[("Binary Files", "*.bin")])
        if file_path:
            combo = getattr(self, target_combo_attr)
            combo['values'] = [file_path]
            combo.set(file_path)

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
        files = os.listdir(BIN_DIR)

        # Application binary files (excluding bootloader and partition files)
        app_bins = [os.path.join(BIN_DIR, f) for f in files if f.endswith('.bin') and 'bootloader' not in f.lower() and 'partition' not in f.lower()]
        current_app_selection = self.bin_combo.get()
        self.bin_combo['values'] = app_bins
        if current_app_selection in app_bins:
            self.bin_combo.set(current_app_selection)
        elif app_bins:
            self.bin_combo.current(0)
        else:
            self.bin_combo.set('')

        # Bootloader binary files
        bootloader_bins = [os.path.join(BIN_DIR, f) for f in files if 'bootloader' in f.lower() and f.endswith('.bin')]
        current_bootloader_selection = self.bootloader_combo.get()
        self.bootloader_combo['values'] = bootloader_bins
        if current_bootloader_selection in bootloader_bins:
            self.bootloader_combo.set(current_bootloader_selection)
        elif bootloader_bins:
            self.bootloader_combo.current(0)
        else:
            self.bootloader_combo.set('')

        # Partition binary files
        partition_bins = [os.path.join(BIN_DIR, f) for f in files if 'partition' in f.lower() and f.endswith('.bin')]
        current_partition_selection = self.partition_combo.get()
        self.partition_combo['values'] = partition_bins
        if current_partition_selection in partition_bins:
            self.partition_combo.set(current_partition_selection)
        elif partition_bins:
            self.partition_combo.current(0)
        else:
            self.partition_combo.set('')

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
        selected_bootloader_bin = self.bootloader_combo.get()
        selected_partition_bin = self.partition_combo.get()

        if not all([selected_port_desc, selected_bin, selected_bootloader_bin, selected_partition_bin]):
            messagebox.showerror("Error", "All fields must be selected.")
            return

        self.flash_button.config(state=tk.DISABLED)
        self.progress_bar.start()

        threading.Thread(
            target=self.run_esptool,
            args=(
                selected_port_desc.split(' - ')[0],
                selected_bin,
                selected_bootloader_bin,
                selected_partition_bin
            ),
            daemon=True
        ).start()

    def run_esptool(self, port, app_bin_file, bootloader_file, partitions_file):
        try:
            self.update_status("Flashing in progress...")
            time.sleep(2)  # Short delay to allow user to press the BOOT button

            # Ensure file paths are absolute
            app_bin_file = os.path.abspath(app_bin_file)
            bootloader_file = os.path.abspath(bootloader_file)
            partitions_file = os.path.abspath(partitions_file)

            # esptool command
            esptool_args = [
                '--chip', 'esp32',
                '--port', port,
                '--baud', '460800',
                '--before', 'default_reset',
                '--after', 'hard_reset',
                'write_flash', '-z',
                '0x1000', bootloader_file,
                '0x8000', partitions_file,
                '0x10000', app_bin_file
            ]

            esptool.main(esptool_args)

            self.update_status("Flashing completed successfully!")
            messagebox.showinfo("Success", "Flashing completed successfully!")

        except Exception as e:
            self.update_status("An error occurred.")
            messagebox.showerror("Error", f"An error occurred:\n{str(e)}")

        finally:
            self.progress_bar.stop()
            self.flash_button.config(state=tk.NORMAL)
            self.refresh_ports()
            self.refresh_bins()

    def update_status(self, message):
        self.status_label.config(text=message)

if __name__ == "__main__":
    root = tk.Tk()
    app = ESPFlasherApp(root)
    root.mainloop()
