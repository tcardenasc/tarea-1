import sys
from PySide6.QtWidgets import ( 
    QApplication, QMainWindow, QLabel, 
    QMessageBox, QComboBox, QProgressBar, 
    QWidget, QTextEdit)
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, QTimer
import PySide6.QtCore as QtCore
import pyqtgraph as pg
from pyqtgraph import PlotWidget
import numpy as np
from components import monitor, bmi270, bme688, interface_class, config
from components.monitor import Monitor
from components.bmi270 import BMI270
from components.bme688 import BME688
from serial.serialutil import SerialException

    # -------- Reminder ----------
    # --- Buttons ---
    # update_config
    # start_data_capture
    # 
    # --- Plots ---
    # Plot1
    # Plot2
    # Plot3
    # Plot4
    #
    # --- Text Inputs ---
    # acc_sampling
    # acc_sensitivity
    # gyr_sampling
    # gyr_sensitivity
    #
    # --- Combo Boxes ---
    # mode_selector
    # sensor_selector
    #
    # --- Progress Bar ---
    # active_progress_bar
from collections import deque
import copy
import time

class PlotWidget(pg.PlotWidget):
    def __init__(self, parent):
        super(PlotWidget, self).__init__()


class Interface(QMainWindow):
    def __init__(self):
        super().__init__()
        from components.interface_class import Ui_Dialog
        from components.config import _config
        self.config_688 = _config["688"]
        self.config_270 = _config["270"]
        self.config_conn = _config["conn"]

        # Load the UI file       
        self.ui = Ui_Dialog()
        self.sensor = None
        self.sensor_control : BME688|BMI270 = None
        self.x_axis = np.linspace(0, 100, 100)

        self.baud = self.config_conn["baud"]
        self.port = self.config_conn["port"]
        self.timeout = self.config_conn["timeout"]
        self.monitor:Monitor = Monitor(self.baud, self.port, self.timeout)
        self.BMI270:BMI270 = BMI270(self, self.monitor, self.config_270)
        self.BME688:BME688 = BME688(self, self.monitor, self.config_688)
        self.tick: QTimer = None

        # Initialize the UI elements and connect signals
        self.init_ui()
        self.BME688.init_ui()
        self.BMI270.init_ui()
        self.monitor.data_init()
        c = 0
        while not self.monitor.connected:
            self.connect_monitor(c)
            c = (c+1) % 4

    def init_ui(self):
        # Connect buttons to functions
        self.ui.setupUi(self)
        self.ui.update_config.clicked.connect(self.update_config)
        self.ui.start_data_capture.clicked.connect(self.start_data_capture)
        self.ui.sensor_selector.currentIndexChanged.connect(self.change_sensor)

    def connect_monitor(self, counter):
        elipsis = "."*counter
        print(f"\rTrying to connect to: {self.port} with baudrate: {self.baud}{elipsis}    ", end="")
        port, _, _ = self.monitor.connect()
        self.port = port
        if self.monitor.connected:
            print(f"\nConnected to: {self.port} with baudrate: {self.baud}", end="")

    def id_sensor(self, modify=False):
        while True:
            if modify:
                self.monitor.send_message("MODIFY_")
            self.monitor.send_message("ID_____")
            time.sleep(0.2)
            try:
                sensor = self.monitor.readline()
            except SerialException:
                time.sleep(0.5)
                return None
            print(sensor)
            if sensor in ["BMI270", "BME688"]:
                break
        return sensor

    #def load_ui(self):
    #    loader = QUiLoader()
    #    ui = loader.load(self.ui_file)
    #    self.setCentralWidget(ui)
    #    self.ui = ui

    def refresh_ui(self):
        # Turn off previous sensor's fields
        if self.sensor_control:
            fields = self.sensor_control.get_fields()
            for key, entry in fields.items():
                ui_field = self.findChild(entry["type"], key)
                ui_field.setEnabled(entry.get("always_enabled", False))
        
        # Turn on current sensor's fields
        self.sensor_control = self.BMI270 if self.sensor == "BMI270" else self.BME688
        fields = self.sensor_control.get_fields()
        for key, entry in fields.items():
            ui_field = self.findChild(entry["type"], key)
            ui_field.setEnabled(True)

        modes = self.sensor_control.refresh_ui(self)
        mode_selector = self.findChild(QComboBox, "mode_selector")
        mode_selector.clear()
        mode_selector.addItems(modes)
        mode_value = self.sensor_control.get_mode()
        mode_selector.setCurrentIndex(mode_value)
        return modes

    def change_sensor(self):
        try:
            self.monitor.send_message("RESET__")
        except SerialException:
            self.monitor= Monitor(self.baud, self.port, self.timeout)
            self.BMI270 = BMI270(self, self.monitor, self.config_270)
            self.BME688 = BME688(self, self.monitor, self.config_688)
            self.monitor.data_init()
            c = 0
            while not self.monitor.connected:
                self.connect_monitor(c)
                c = (c+1) % 4

        sensor = self.read_combo_box("sensor_selector")
        if self.sensor == sensor:
            return sensor
        if sensor != "<None>":
            self.sensor = self.id_sensor()
        else:
            self.sensor = None
        if not self.sensor:
            return None

        for _ in range(1):
            self.monitor.send_message("OK_____")
            if self.monitor.sem_status() == 0:
                self.monitor.go()    
        # Detected new sensor
        # Change options of mode_selector combo box
        self.refresh_ui()
        return sensor

    def update_config(self):
        self.read_all_config()
        
        # Check if sensor has changed, if not proceed
        # sensor = self.change_sensor()
        # if not self.sensor:
        #     return
        # if self.sensor != sensor:
        #     QMessageBox.information(self, "Mismatching Sensor Detected", f"Sensor Requested: {sensor}\nSensor Detected: {self.sensor}")
        #     return
        
        # Send config to sensor
        first_time = True
        while self.sensor != (new := self.id_sensor(modify=True)):
            print(f"Mismatching Sensor Detected: expected {self.sensor} got: {new}" )
            self.monitor.send_message("RESET__") if not first_time else None
            time.sleep(0.1)
            first_time = False
        if self.sensor == "BMI270":
            self.BMI270.update_config(self.config_270)
        elif self.sensor == "BME688":
            self.BME688.update_config(self.config_688)
        # Change ui options according to the sensor
        self.refresh_ui()

        # Set up timer to read data
        self.tick = QTimer()
        self.tick.timeout.connect(self.sensor_control.cycle)


    def start_data_capture(self):
        if self.sensor_control is None or self.tick is None:
            print(self.sensor_control, self.tick)
            return
        if self.monitor.sem_status() == 0:
            self.monitor.go()
        self.sensor_control.start_data_capture(self) # Clean plots and cache
        # Start monitor
        self.tick.start(10)

    # Plot data
    def plot(self, plot:PlotWidget, cache: dict):
        plot.plot(self.x_axis, cache["y_axis"], pen=cache["color"])

    def read_input(self, input_name: str, object_type: QWidget, default = 0):
        read = self.findChild(object_type, input_name)
        output = None
        if   object_type is QTextEdit: output = read.toPlainText()
        elif object_type is QComboBox: output = read.currentText()
        elif object_type is QProgressBar: output = read.value()
        else: raise KeyError(f"Invalid Config Type: {input_name} is {object_type}")
        if not output:
            output = default
        return output
    
    def read_combo_box(self, combo_box_name: str):
        # Placeholder: Get selected item from a combo box and display it
        combo_box = self.findChild(QComboBox, combo_box_name)
        
        selected_item = combo_box.currentText()
        return selected_item

    def read_progress_bar(self, progress_bar_name: str):
        # Placeholder: Get the value of a progress bar and display it
        progress_bar = self.findChild(QProgressBar, progress_bar_name)
        value = progress_bar.value()
        return value
    
    def read_all_config(self):
        if not self.sensor:
            return
        if self.sensor == "BMI270":
            for key in self.config_270['fields']:
                entry = self.config_270['fields'][key]
                self.config_270['fields'][key]["value"] = self.read_input(key, entry["type"], entry["default"])
            
        if self.sensor == "BME688":
            for key in self.config_688['fields']:
                entry = self.config_688['fields'][key]
                self.config_688['fields'][key]["value"] = self.read_input(key, entry["type"], entry["default"])
    


if __name__ == "__main__":
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)
    app = QApplication(sys.argv)
    window = Interface()
    window.show()
    sys.exit(app.exec())

