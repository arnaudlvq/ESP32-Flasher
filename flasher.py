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
        self.update_combo(self.port_combo, port_list)

    def refresh_bins(self):
        if not os.path.exists(BIN_DIR):
            os.makedirs(BIN_DIR)
        files = os.listdir(BIN_DIR)

        app_bins = [f for f in files if f.endswith('.bin') and 'bootloader' not in f.lower() and 'partition' not in f.lower()]
        self.update_combo(self.bin_combo, app_bins)

        bootloader_bins = [f for f in files if 'bootloader' in f.lower() and f.endswith('.bin')]
        self.update_combo(self.bootloader_combo, bootloader_bins)

        partition_bins = [f for f in files if 'partition' in f.lower() and f.endswith('.bin')]
        self.update_combo(self.partition_combo, partition_bins)

    def update_combo(self, combo, values):
        current_selection = combo.get()
        combo['values'] = values
        if current_selection in values:
            combo.set(current_selection)
        elif values:
            combo.current(0)
        else:
            combo.set('')

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
            args=(selected_port_desc.split(' - ')[0], selected_bin, selected_bootloader_bin, selected_partition_bin),
            daemon=True
        ).start()

    def run_esptool(self, port, app_bin_file, bootloader_file, partitions_file):
        try:
            self.update_status("Flashing in progress...")
            time.sleep(2)

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
