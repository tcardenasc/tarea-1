from PySide6.QtWidgets import (
    QApplication, QMainWindow, QLabel, 
    QMessageBox, QComboBox, QProgressBar, 
    QWidget, QTextEdit)

x_full = 100
x_peak = 5
config_ui_270_fields = {
    "acc_sampling": {
        "type" : QComboBox,
        "value": 0,
        "default": 0,
        "always_enabled": False
    },
    "acc_sensitivity": {
        "type" : QComboBox,
        "value": 0,
        "default": 0,
        "always_enabled": False
    },
    "gyr_sampling": {
        "type" : QComboBox,
        "value": 0,
        "default": 0,
        "always_enabled": False
    },
    "gyr_sensitivity": {
        "type" : QComboBox,
        "value": 0,
        "default": 0,
        "always_enabled": False
    },
    "mode_selector": {
        "type" : QComboBox,
        "value": 0,
        "default": 0,
        "always_enabled": True
    },
    "sensor_selector": {
        "type" : QComboBox,
        "value": 0,
        "default": 0,
        "always_enabled": True
    },
    "active_progress_bar": {
        "type" : QProgressBar,
        "value": 0,
        "default": 0,
        "always_enabled": True
    }
}

config_ui_270 = {
    "fields" : config_ui_270_fields,
    "modes" : ["Low Power", "Normal Power", "Performance", "Suspend"],
    "acc_odr_hex" : {
        "25/32": 1, "25/16": 2, "25/8": 3,
        "25/4": 4, "25/2": 5, "25": 6,
        "50": 7, "100": 8, "200": 9,
        "400": 10, "800": 11, "1600": 12
        },
    "gyr_odr_hex" : {
        "25": 6, "50": 7, "100": 8, 
        "200": 9, "400": 10, "800": 11,
        "1600": 12, "3200": 13
        },
    "acc_snb_hex" : {
        "+/- 2g": 0, "+/- 4g": 1,
        "+/- 8g": 2, "+/- 16g": 3 
    },
    "gyr_snb_hex" : {
        "+/- 2000dps": 0, "+/- 1000dps": 1,
        "+/- 500dps": 2, "+/- 250dps": 3, "+/- 125dps": 4
    },
    "plots": ["Accelerometer (m/s²)", "Gyroscope (rad/s)" ,"RMS", "FFT"],
    "plot_series": [
        { # Graph accelerometer
            "x": {
                "y_axis": [],
                "color": "r",
                "x_size": x_full,
                },
            "y": {
                "y_axis": [],
                "color": "g",
                "x_size": x_full,
            },
            "z": {
                "y_axis": [],
                "color": "b",
                "x_size": x_full,
            },
            "peak_x" : {
                "y_axis": [],
                "color": "r",
                "x_size": x_peak,
            },
            "peak_y" : {
                "y_axis": [],
                "color": "g",
                "x_size": x_peak,
            },
            "peak_z" : {
                "y_axis": [],
                "color": "b",
                "x_size": x_peak,
            }
        },
        { # Graph Gyroscope 
            "x": {
                "y_axis": [],
                "color": "r",
                "x_size": x_full,
                },
            "y": {
                "y_axis": [],
                "color": "g",
                "x_size": x_full,
            },
            "z": {
                "y_axis": [],
                "color": "b",
                "x_size": x_full,
            },
            "peak_x" : {
                "y_axis": [],
                "color": "r",
                "x_size": x_peak,
            },
            "peak_y" : {
                "y_axis": [],
                "color": "g",
                "x_size": x_peak,
            },
            "peak_z" : {
                "y_axis": [],
                "color": "b",
                "x_size": x_peak,
            }},
        { # Graph RMS
            "acc_x": {
                "y_axis": [],
                "color": "r",
                "x_size": x_full,
                },
            "acc_y": {
                "y_axis": [],
                "color": "g",
                "x_size": x_full,
            },
            "acc_z": {
                "y_axis": [],
                "color": "b",
                "x_size": x_full,
            },
            "gyr_x": {
                "y_axis": [],
                "color": "m",
                "x_size": x_full,
                },
            "gyr_y": {
                "y_axis": [],
                "color": "y",
                "x_size": x_full,
            },
            "gyr_z": {
                "y_axis": [],
                "color": "c",
                "x_size": x_full,
            },
        },
        { # Graph FFT
            "acc_x": {
                "y_axis": [],
                "color": "r",
                "x_size": x_full,
                },
            "acc_y": {
                "y_axis": [],
                "color": "g",
                "x_size": x_full,
            },
            "acc_z": {
                "y_axis": [],
                "color": "b",
                "x_size": x_full,
            },
            "gyr_x": {
                "y_axis": [],
                "color": "m",
                "x_size": x_full,
                },
            "gyr_y": {
                "y_axis": [],
                "color": "y",
                "x_size": x_full,
            },
            "gyr_z": {
                "y_axis": [],
                "color": "c",
                "x_size": x_full,
            },
        }
    ]
}

config_ui_688_fields = {
    "mode_selector": {
        "type" : QComboBox,
        "value": 0,
        "default": 0,
        "always_enabled": True
    },
    "sensor_selector": {
        "type" : QComboBox,
        "value": 0,
        "default": 0,
        "always_enabled": True
    },
    "active_progress_bar": {
        "type" : QProgressBar,
        "value": 0,
        "default": 0,
        "always_enabled": True
    }
}

config_ui_688 = {
    "fields": config_ui_688_fields,
    "modes": ["Forced", "Parallel", "Sleep"],
    "plots" : ["Temperature (°C)", "Humidity (%)", "Pressure (Pa)", "Air Pollution  (Ω)"],
    "plot_series": [
        { # Graph Temperature
            "temperature": {
                "y_axis": [],
                "color": "r",
                "x_size": x_full,
                },
            "peak_temperature" : {
                "y_axis": [],
                "color": "r",
                "x_size": x_peak,
            }
        },
        { # Graph Humidity
            "humidity": {
                "y_axis": [],
                "color": "g",
                "x_size": x_full,
                },
            "peak_humidity" : {
                "y_axis": [],
                "color": "g",
                "x_size": x_peak,
            }
        },
        { # Graph Pressure
            "pressure": {
                "y_axis": [],
                "color": "b",
                "x_size": x_full,
                },
            "peak_pressure" : {
                "y_axis": [],
                "color": "b",
                "x_size": x_peak,
            }
        },
        { # Graph Air Pollution Concentration
            "air_pollution_concentration": {
                "y_axis": [],
                "color": "m",
                "x_size": x_full,
                },
            "peak_air_pollution_concentration" : {
                "y_axis": [],
                "color": "m",
                "x_size": x_peak,
            }
        }
    ]
}

connection = {
    "port": "/dev/ttyUSB0",
    "baud": 115200,
    "timeout": 1,}

_config = {
    "270": config_ui_270,
    "688": config_ui_688,
    "conn": connection
}