import sys
import os
import time
import serial.tools.list_ports
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGroupBox, QLabel, QComboBox, QPushButton, QProgressBar, QMessageBox,
    QFileDialog, QTextEdit
)
from PySide6.QtCore import QThread, Signal, QObject, Slot
from PySide6.QtGui import QFont

# Determine the base path for resources (like the 'bin' directory)
if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    # Running as a bundled app (.app)
    # The path needs to go up from .../Flasher.app/Contents/MacOS/Flasher
    base_path = os.path.abspath(os.path.join(os.path.dirname(sys.executable), '..', '..', '..'))
else:
    # Running as a normal python script
    base_path = os.path.dirname(os.path.abspath(__file__))

BIN_DIR = os.path.join(base_path, 'bin')  # Directory where the binary files are located

class StdoutEmitter(QObject):
    textWritten = Signal(str)

    def write(self, text):
        self.textWritten.emit(str(text))

    def flush(self):
        pass

class EsptoolWorker(QObject):
    """
    Worker thread for running esptool as a Python library to avoid freezing the GUI.
    """
    output = Signal(str)
    finished = Signal(int)

    def __init__(self, args):
        super().__init__()
        self.args = args

    def run(self):
        """
        Executes the esptool command by calling its main function and
        redirecting stdout to capture output in real-time.
        """
        original_stdout = sys.stdout
        original_stderr = sys.stderr
        
        emitter = StdoutEmitter()
        # Connect the emitter's signal to the worker's output signal
        emitter.textWritten.connect(lambda text: self.output.emit(text.strip()))

        sys.stdout = emitter
        sys.stderr = emitter
        
        exit_code = 0
        try:
            import esptool
            esptool.main(self.args)
        except SystemExit as e:
            # esptool calls sys.exit() on completion. 0 is success.
            exit_code = e.code if e.code is not None else 0
        except Exception as e:
            # Print any other exceptions to our redirected output
            print(f"An error occurred while running esptool:\n{str(e)}")
            exit_code = 1
        finally:
            # Always restore the original stdout/stderr
            sys.stdout = original_stdout
            sys.stderr = original_stderr

        self.finished.emit(exit_code)

    def stop(self):
        pass


class PortMonitor(QObject):
    """Monitors serial port connections in a background thread."""
    ports_changed = Signal()

    def __init__(self):
        super().__init__()
        self._running = True
        self._previous_ports = set()

    def run(self):
        while self._running:
            try:
                ports = set(p.device for p in serial.tools.list_ports.comports())
                if ports != self._previous_ports:
                    self._previous_ports = ports
                    self.ports_changed.emit()
            except Exception:
                # Ignore errors during port scanning
                pass
            time.sleep(1)

    def stop(self):
        self._running = False


class ESPFlasherApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ESP32 Flasher")
        self.setGeometry(100, 100, 700, 600)

        self.esptool_thread = None
        self.esptool_worker = None

        self.create_widgets()
        self.refresh_ports()
        self.refresh_bins()

        self.start_port_monitor()

    def create_widgets(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)

        # Port selection
        port_group = QGroupBox("Select COM Port")
        port_layout = QHBoxLayout(port_group)
        self.port_combo = QComboBox()
        self.port_combo.setMinimumWidth(300)
        refresh_ports_button = QPushButton("Refresh")
        refresh_ports_button.clicked.connect(self.refresh_ports)
        port_layout.addWidget(self.port_combo)
        port_layout.addWidget(refresh_ports_button)
        main_layout.addWidget(port_group)

        # Binary file selection
        file_group = QGroupBox("Select Binary Files")
        file_layout = QVBoxLayout(file_group)
        self.bootloader_combo = self.create_file_selection(file_layout, "Bootloader:")
        self.partition_combo = self.create_file_selection(file_layout, "Partitions:")
        self.ota_data_combo = self.create_file_selection(file_layout, "OTA Data:")
        self.bin_combo = self.create_file_selection(file_layout, "Application:")
        main_layout.addWidget(file_group)

        # Flash button and progress bar
        action_group = QGroupBox("Actions")
        action_layout = QHBoxLayout(action_group)
        self.flash_button = QPushButton("Flash ESP32")
        self.flash_button.clicked.connect(self.flash_esp32)
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Indeterminate
        self.progress_bar.hide()
        action_layout.addWidget(self.flash_button)
        action_layout.addWidget(self.progress_bar)
        main_layout.addWidget(action_group)

        # Output console
        output_group = QGroupBox("Output")
        output_layout = QVBoxLayout(output_group)
        self.output_console = QTextEdit()
        self.output_console.setReadOnly(True)
        self.output_console.setFont(QFont("Courier", 10))
        output_layout.addWidget(self.output_console)
        main_layout.addWidget(output_group)

        # Status label
        self.status_label = QLabel("Ready")
        main_layout.addWidget(self.status_label)

    def create_file_selection(self, parent_layout, label_text):
        row_layout = QHBoxLayout()
        label = QLabel(label_text)
        label.setMinimumWidth(80)
        combobox = QComboBox()
        browse_button = QPushButton("Browse...")
        
        row_layout.addWidget(label)
        row_layout.addWidget(combobox)
        row_layout.addWidget(browse_button)
        parent_layout.addLayout(row_layout)

        browse_button.clicked.connect(lambda: self.browse_file(combobox))
        return combobox

    def browse_file(self, combobox):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Binary File", BIN_DIR, "Binary Files (*.bin)")
        if file_path:
            if combobox.findText(file_path) == -1:
                 combobox.addItem(file_path)
            combobox.setCurrentText(file_path)

    @Slot()
    def refresh_ports(self):
        ports = serial.tools.list_ports.comports()
        port_list = [f"{port.device} - {port.description}" for port in ports]
        current_selection = self.port_combo.currentText()
        self.port_combo.clear()
        self.port_combo.addItems(port_list)
        if current_selection in port_list:
            self.port_combo.setCurrentText(current_selection)

    def refresh_bins(self):
        if not os.path.exists(BIN_DIR):
            os.makedirs(BIN_DIR)
        
        files = [os.path.join(BIN_DIR, f) for f in os.listdir(BIN_DIR) if f.endswith('.bin')]
        
        app_bins = [f for f in files if 'bootloader' not in f.lower() and 'partition' not in f.lower() and 'boot_app0' not in f.lower()]
        bootloader_bins = [f for f in files if 'bootloader' in f.lower()]
        partition_bins = [f for f in files if 'partition' in f.lower()]
        ota_data_bins = [f for f in files if 'boot_app0' in f.lower()]

        self.update_combo_box(self.bin_combo, app_bins)
        self.update_combo_box(self.bootloader_combo, bootloader_bins)
        self.update_combo_box(self.partition_combo, partition_bins)
        self.update_combo_box(self.ota_data_combo, ota_data_bins)

    def update_combo_box(self, combobox, items):
        current_text = combobox.currentText()
        combobox.clear()
        combobox.addItems(items)
        if current_text in items:
            combobox.setCurrentText(current_text)
        elif items:
            combobox.setCurrentIndex(0)

    def start_port_monitor(self):
        self.port_monitor_thread = QThread()
        self.port_monitor = PortMonitor()
        self.port_monitor.moveToThread(self.port_monitor_thread)
        self.port_monitor.ports_changed.connect(self.refresh_ports)
        self.port_monitor_thread.started.connect(self.port_monitor.run)
        self.port_monitor_thread.start()

    def closeEvent(self, event):
        self.port_monitor.stop()
        self.port_monitor_thread.quit()
        self.port_monitor_thread.wait()
        
        # The esptool function call cannot be forcefully stopped.
        # We just wait for the thread to finish its work if it's running.
        if self.esptool_thread and self.esptool_thread.isRunning():
            self.esptool_thread.quit()
            self.esptool_thread.wait()

        super().closeEvent(event)

    def flash_esp32(self):
        selected_port_desc = self.port_combo.currentText()
        selected_bootloader = self.bootloader_combo.currentText()
        selected_partition = self.partition_combo.currentText()
        selected_ota_data = self.ota_data_combo.currentText()
        selected_bin = self.bin_combo.currentText()

        if not all([selected_port_desc, selected_bootloader, selected_partition, selected_ota_data, selected_bin]):
            QMessageBox.critical(self, "Error", "All binary files and a COM port must be selected.")
            return

        self.flash_button.setEnabled(False)
        self.progress_bar.show()
        self.status_label.setText("Flashing in progress...")
        self.output_console.clear()

        port = selected_port_desc.split(' - ')[0]

        esptool_args = [
            '--chip', 'esp32c3',
            '--port', port,
            '--baud', '921600',
            '--before', 'default-reset',
            '--after', 'hard-reset',
            'write_flash',
            '--flash-mode', 'keep',
            '--flash-freq', 'keep',
            '--flash-size', 'keep',
            '-z',
            '0x0', os.path.abspath(selected_bootloader),
            '0x8000', os.path.abspath(selected_partition),
            '0xe000', os.path.abspath(selected_ota_data),
            '0x10000', os.path.abspath(selected_bin)
        ]
        
        self.esptool_thread = QThread()
        self.esptool_worker = EsptoolWorker(esptool_args)
        self.esptool_worker.moveToThread(self.esptool_thread)

        self.esptool_worker.output.connect(self.append_output)
        self.esptool_worker.finished.connect(self.on_flash_finished)
        self.esptool_thread.started.connect(self.esptool_worker.run)
        
        # Clean up thread and worker
        self.esptool_worker.finished.connect(self.esptool_thread.quit)
        self.esptool_worker.finished.connect(self.esptool_worker.deleteLater)
        self.esptool_thread.finished.connect(self.esptool_thread.deleteLater)

        self.esptool_thread.start()

    @Slot(str)
    def append_output(self, text):
        self.output_console.append(text)

    @Slot(int)
    def on_flash_finished(self, exit_code):
        self.progress_bar.hide()
        self.flash_button.setEnabled(True)
        
        if exit_code == 0:
            self.status_label.setText("Flashing completed successfully!")
            QMessageBox.information(self, "Success", "Flashing completed successfully!")
        else:
            self.status_label.setText("Flashing failed!")
            QMessageBox.critical(self, "Error", "Flashing failed. Check the output console for details.")

        self.refresh_ports()
        self.refresh_bins()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ESPFlasherApp()
    window.show()
    sys.exit(app.exec())
