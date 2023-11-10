import pyqtgraph as pg
import numpy as np
import time
try:
    from components.monitor import Monitor
except:
    from monitor import Monitor
from PySide6.QtWidgets import ( 
    QApplication, QMainWindow, QLabel, 
    QMessageBox, QComboBox, QProgressBar, 
    QWidget, QTextEdit)
class BME688():
    def __init__(self, ui, monitor, configs) -> None:
        self.plots = []
        self.cache:dict[str, dict[str, dict]] = {}
        self.ui = ui
        self.monitor: Monitor = monitor
        self.config = configs
        self.full_x_axis = np.linspace(0, 100, 100)
        self.peak_x_axis = np.linspace(0, 100, 5)

    def init_ui(self):
        ui = self.ui.ui
        
        self.plots = [ui.Plot1, ui.Plot2, ui.Plot3, ui.Plot4]
        for i, plot in enumerate(self.plots):
            # each graph contains it's serie's data
            self.cache[plot] = self.config["plot_series"][i] # {"x": {}, "y": {}, "z": {}}

            # for each ("x", {"y_axis" : ..., "color": ... "x_size": ...}) , ...
            for serie_name, serie_data in self.cache[plot].items():
                    data_len = serie_data["x_size"]
                    self.cache[plot][serie_name]["y_axis"] = np.zeros(data_len)

    def refresh_ui(self, window):
        modes = self.config["modes"]

        # Set graph labels and clear graphs
        plot_titles = self.config["plots"]
        plot_labels = ["plot1_label", "plot2_label", "plot3_label", "plot4_label"]
        for label, title,  plot in zip(plot_labels, plot_titles, self.plots[:4]):
            window.findChild(QLabel, label).setText(title)
            for series in self.cache[plot].keys():
                is_line = (self.cache[plot][series]["x_size"] == len(self.full_x_axis)) 
                if is_line:
                    window.plot(plot, self.cache[plot][series])
        # return mode selector options for interface to update
        return modes

    def get_fields(self) -> dict:
        fields = self.config["fields"]
        return fields
    
    def get_modes(self) -> list:
        modes = self.config["modes"]
        return modes

    def get_mode(self):
        mode = 0
        try:
            mode = self.config["modes"].index(self.config["fields"]["mode_selector"]["value"])
        except: pass
        return mode

    def start_data_capture(self, window):
        interface = window
        # Clean plots and cache
        for plot in self.plots:
            plot.clear()
            for serie in self.cache[plot].keys():
                self.cache[plot][serie]["y_axis"] = np.zeros_like(self.cache[plot][serie]["y_axis"])
                is_line = (self.cache[plot][serie]["x_size"] == len(self.full_x_axis)) 
                if is_line:
                    interface.plot(plot, self.cache[plot][serie])
        
        # Start monitor
        self.monitor.set_sensor("BME688")
        self.monitor.start()
    
    def append_data(self, list, data):
        list = np.append(list[len(data):], data)

    # Fetch data and plot
    def cycle(self):
        print("cycle", end="")
        if self.monitor.sem_status() == 0:
            return
        print("-", end="")
        interface = self.ui
        for plot in self.plots:
            plot.clear()
        
        data = self.monitor.get_BME688_data()
        # print("cycle: ", data)
        data_by_graph = [
            data["temp"] + data["temp_peaks"],
            data["hum"] + data["hum_peaks"],
            data["press"] + data["press_peaks"],
            data["co2"] + data["co2_peaks"]
        ]
        # for each plot cache and data cache
        for plot, data in zip(self.plots, data_by_graph):
            scatter = pg.ScatterPlotItem()
            # for each data series in plot, update cache and plot
            for serie, serie_data in zip(self.cache[plot].keys(), data):
                self.cache[plot][serie]["y_axis"] = serie_data
                is_line = (self.cache[plot][serie]["x_size"] == len(self.full_x_axis)) # else is scatter plot
                if is_line:
                    interface.plot(plot, self.cache[plot][serie])
                else:
                    scatter.addPoints(x=self.peak_x_axis, 
                                    y=self.cache[plot][serie]["y_axis"], 
                                    brush=self.cache[plot][serie]["color"],
                                    size=5)

            plot.addItem(scatter)
        print("\n")

    def update_config(self, config):
        pwr_mode = self.get_mode() + 1
        pwr_command = f"PWR#{pwr_mode}__"

        print(pwr_command)
        self.monitor.send_message(pwr_command)
        time.sleep(0.2)
