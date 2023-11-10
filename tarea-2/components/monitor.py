from threading import Thread, Semaphore
from serial import Serial
import serial.serialutil
from struct import pack
#import scipy.fftpack.fft as fft
import numpy as np
import serial
import time
import sys

class Monitor():
    def __init__(self, baud, port, timeout) -> None:
        self.serial = None
        self.cache = b''
        self.baud = baud
        self.port = port
        self.timeout = timeout
        self.connected = False
        self.running = False
        self.sensor = None
        self.decode_channel = {
            "BMI270": self.do_BMI270,
            "BME688": self.do_BME688
        }
        self.bmi_270_data = {
            "araw":     [[],[],[]], # G1
            "graw":     [[],[],[]], # G2
            "arms":     [[],[],[]], # G3 
            "grms":     [[],[],[]], # G3
            "afft":     [[],[],[]], # G4
            "gfft":     [[],[],[]], # G4
            "apeaks":   [[],[],[]], # G1
            "gpeaks":   [[],[],[]], # G2
        }
        self.bme_688_data = {
            "temp":  [[]],  # G1
            "hum":   [[]],  # G2
            "press": [[]],  # G3
            "co2":   [[]],  # G4
            "temp_peaks":  [[]],  # G1
            "hum_peaks":   [[]],  # G2
            "press_peaks": [[]],  # G3
            "co2_peaks":   [[]]   # G4
        }
        self.thread = None
        self.sem = Semaphore(0)
        self.sensor_names = ["BMI270", "BME688"]
        self.connection_attempts = 0

    def data_init(self):
        for serie in list(self.bmi_270_data.keys())[0:6]:
            for axis in range(3):
                self.bmi_270_data[serie][axis] = np.zeros(100)
        for serie in list(self.bmi_270_data.keys())[6:]:
            for axis in range(3):
                self.bmi_270_data[serie][axis] = np.zeros(5)
        for serie in list(self.bme_688_data.keys())[0:4]:
            self.bme_688_data[serie][0] = np.zeros(100)
        for serie in list(self.bme_688_data.keys())[4:]:
            self.bme_688_data[serie][0] = np.zeros(5)

    def connect(self):
        try:
            self.serial = Serial(self.port, self.baud, timeout=self.timeout)
            self.connected = True
        except:
            self.connected = False
            self.connection_attempts = (self.connection_attempts + 1) % 4
            if not self.connection_attempts:
                port_number = int(self.port[-1])
                self.port = self.port[:-1] + str(int(not port_number))
        return self.port, self.baud, self.timeout
    
    def set_sensor(self, sensor):
        self.sensor = sensor

    def start(self):
        for _ in range(1):
            self.send_message("BEGIN__")
        if self.running:
            return
        self.running = True
        self.thread = Thread(target=self.process)
        self.thread.start()
    
    def process(self):
        print("Read Process Started")
        if not self.connected or not self.sensor:
            print("Not Connected or Sensor not set")
            self.wait()
        print("Connected and Sensor Set")
        time.sleep(1.0)
        while self.running:
            self.cycle()

    def cycle(self):
        received = ''
        if not self.connected:
            print("Connection Lost")
            self.wait()
        try:
            received = self.serial.read_until(b'>')
            for sensor in self.sensor_names:
                if sensor in received.decode():
                    if sensor == self.sensor:
                        self.send_message("OK_____")
                    else:
                        self.send_message("RESET__")
        except serial.SerialTimeoutException:
            print("Timeout")
            self.connected = False
            self.sensor = None
            return
        except serial.serialutil.SerialException:
            print("Disconnected")
            self.connected = False
            self.sensor = None
            return 
        try:
            self.decode_n_save(received)
            self.connected = True
        except Exception as e:
            
            with open('error.log', 'ba') as f:
               f.write(received)
            if received:
                print("Decode Error - ", e, '\n\n================',received, '================\n\n')
            import traceback  
            #traceback.print_exc()
            #self.connected = False  

    def do_BMI270(self, data):
        data = self.decode_BMI270(data)
        self.store_BMI270(data)

    def do_BME688(self, data):
        data = self.decode_BME688(data)
        self.store_BME688(data)

    def decode_BMI270(self, data):
        data = data.decode("utf-8")
        # data = data.split('<')[1].split('>')[0].split('|')
        data = data.split('<')
        data = data[1].split('>')
        data = data[0].split('|')
        
        vals, rms_vals, fts, peaks = data
        
        vals = vals.split('\t')
        rms_vals = rms_vals.split('\t')
        fts = fts.split('\t')
        peaks = peaks.split('&')

        vals = convert_value_data(vals, int)
        rms_vals = convert_value_data(rms_vals, float)
        fts = convert_complex_data(fts)

        peaks_accx = convert_value_data(peaks[0].split('\t'),float)*(78.4532/32768)
        peaks_accy = convert_value_data(peaks[1].split('\t'),float)*(78.4532/32768)
        peaks_accz = convert_value_data(peaks[2].split('\t'),float)*(78.4532/32768)
        peaks_gyrx = convert_value_data(peaks[3].split('\t'),float)*(34.90659/32768)
        peaks_gyry = convert_value_data(peaks[4].split('\t'),float)*(34.90659/32768)
        peaks_gyrz = convert_value_data(peaks[5].split('\t'),float)*(34.90659/32768)

        acc_x, acc_y, acc_z, gyr_x, gyr_y, gyr_z = vals

        acc_x = acc_x*(78.4532/32768)
        acc_y = acc_y*(78.4532/32768)
        acc_z = acc_z*(78.4532/32768)

        gyr_x = gyr_x*(34.90659/32768)
        gyr_y = gyr_y*(34.90659/32768)
        gyr_z = gyr_z*(34.90659/32768)

        acc_raw = [acc_x, acc_y, acc_z]
        gyr_raw = [gyr_x, gyr_y, gyr_z]
        acc_peaks = [peaks_accx, peaks_accy, peaks_accz]
        gyr_peaks = [peaks_gyrx, peaks_gyry, peaks_gyrz]
        peaks = (acc_peaks, gyr_peaks)

        abs_fts = np.array(fts)
        abs_fts = np.abs(abs_fts)
        # map abs_fts to an array of 6 arrays of 100 elements each
        abs_fts_resized = []

        # Interpolate each array to the desired length
        for array in abs_fts:
            x_old = np.linspace(0, 1, len(array))
            x_new = np.linspace(0, 1, 100)
            interpolated_array = np.interp(x_new, x_old, array)
            abs_fts_resized.append(interpolated_array)

        # Convert the list of arrays into a NumPy array
        abs_fts = np.array(abs_fts_resized)

        return acc_raw, gyr_raw, rms_vals, abs_fts, peaks

    def decode_BME688(self, data):
        data = data.decode("utf-8")
        # print("trying to split <:", data)
        data = data.split('<')
        # print("trying to split >:", data)
        data = data[1].split('>')
        # print("trying to split |:", data)
        data = data[0].split('|')

        vals, peaks = data

        temp, hum, press, co2, _ = vals.split('&')
        temp_peaks, hum_peaks, press_peaks, co2_peaks, _ = peaks.split('&')

        temp  = convert_value_data(temp.split('\t')[:-1], float)
        hum   = convert_value_data(hum.split('\t')[:-1], float)
        press = convert_value_data(press.split('\t')[:-1], float)
        co2   = convert_value_data(co2.split('\t')[:-1], float)

        temp_peaks  = convert_value_data(temp_peaks.split('\t'), float)
        hum_peaks   = convert_value_data(hum_peaks.split('\t'), float)
        press_peaks = convert_value_data(press_peaks.split('\t'), float)
        co2_peaks   = convert_value_data(co2_peaks.split('\t'), float)

        return (temp, hum, press, co2), (temp_peaks, hum_peaks, press_peaks, co2_peaks)

    def append_data(self, list, data):
        list = np.append(list[len(data):], data)
        return list

    def store_BMI270(self, data):
        araw, graw, rms, fft, peaks = data
        araw_x, araw_y, araw_z = araw
        graw_x, graw_y, graw_z = graw
        arms_x, arms_y, arms_z, grms_x, grms_y, grms_z  = rms
        afft_x, afft_y, afft_z, gfft_x, gfft_y, gfft_z = fft
        apeaks, gpeaks = peaks
        apeaks_x, apeaks_y, apeaks_z = apeaks
        gpeaks_x, gpeaks_y, gpeaks_z = gpeaks

        self.bmi_270_data["araw"][0] = self.append_data(self.bmi_270_data["araw"][0], [araw_x]) # append(list, val) CAMBIAR ESTO a append(list, list)
        self.bmi_270_data["araw"][1] = self.append_data(self.bmi_270_data["araw"][1], [araw_y])
        self.bmi_270_data["araw"][2] = self.append_data(self.bmi_270_data["araw"][2], [araw_z])

        self.bmi_270_data["graw"][0] = self.append_data(self.bmi_270_data["graw"][0], [graw_x])
        self.bmi_270_data["graw"][1] = self.append_data(self.bmi_270_data["graw"][1], [graw_y])
        self.bmi_270_data["graw"][2] = self.append_data(self.bmi_270_data["graw"][2], [graw_z])
        
        self.bmi_270_data["arms"][0] = self.append_data(self.bmi_270_data["arms"][0], [arms_x]) # append(list, val) ESTO ES ASI
        self.bmi_270_data["arms"][1] = self.append_data(self.bmi_270_data["arms"][1], [arms_y])
        self.bmi_270_data["arms"][2] = self.append_data(self.bmi_270_data["arms"][2], [arms_z])
        
        self.bmi_270_data["grms"][0] = self.append_data(self.bmi_270_data["grms"][0], [grms_x])
        self.bmi_270_data["grms"][1] = self.append_data(self.bmi_270_data["grms"][1], [grms_y])
        self.bmi_270_data["grms"][2] = self.append_data(self.bmi_270_data["grms"][2], [grms_z])
        
        self.bmi_270_data["afft"][0] = afft_x #self.append_data(self.bmi_270_data["afft"][0], afft_x) # append(list, list) ESTO ES ASI
        self.bmi_270_data["afft"][1] = afft_y #self.append_data(self.bmi_270_data["afft"][1], afft_y)
        self.bmi_270_data["afft"][2] = afft_z #self.append_data(self.bmi_270_data["afft"][2], afft_z)

        self.bmi_270_data["gfft"][0] = gfft_x #self.append_data(self.bmi_270_data["gfft"][0], gfft_x)
        self.bmi_270_data["gfft"][1] = gfft_y #self.append_data(self.bmi_270_data["gfft"][1], gfft_y)
        self.bmi_270_data["gfft"][2] = gfft_z #self.append_data(self.bmi_270_data["gfft"][2], gfft_z)
        
        self.bmi_270_data["apeaks"][0] = np.sort(np.append(self.bmi_270_data["apeaks"][0], apeaks_x))[5:] # append(list, list) ESTO ES ASI
        self.bmi_270_data["apeaks"][1] = np.sort(np.append(self.bmi_270_data["apeaks"][1], apeaks_y))[5:]
        self.bmi_270_data["apeaks"][2] = np.sort(np.append(self.bmi_270_data["apeaks"][2], apeaks_z))[5:]
        
        self.bmi_270_data["gpeaks"][0] = np.sort(np.append(self.bmi_270_data["gpeaks"][0], gpeaks_x))[5:]
        self.bmi_270_data["gpeaks"][1] = np.sort(np.append(self.bmi_270_data["gpeaks"][1], gpeaks_y))[5:]
        self.bmi_270_data["gpeaks"][2] = np.sort(np.append(self.bmi_270_data["gpeaks"][2], gpeaks_z))[5:]

    def store_BME688(self, data):
        vals, peaks = data
        temp, hum, press, co2 = vals 
        temp_peaks, hum_peaks, press_peaks, co2_peaks = peaks
        
        self.bme_688_data["temp"][0]        = self.append_data(self.bme_688_data["temp"][0],temp)
        self.bme_688_data["hum"][0]         = self.append_data(self.bme_688_data["hum"][0],hum)
        self.bme_688_data["press"][0]       = self.append_data(self.bme_688_data["press"][0],press)
        self.bme_688_data["co2"][0]         = self.append_data(self.bme_688_data["co2"][0],co2)

        self.bme_688_data["temp_peaks"][0]  = np.sort(np.append(self.bme_688_data["temp_peaks"][0],temp_peaks))[5:]
        self.bme_688_data["hum_peaks"][0]   = np.sort(np.append(self.bme_688_data["hum_peaks"][0],hum_peaks))[5:]
        self.bme_688_data["press_peaks"][0] = np.sort(np.append(self.bme_688_data["press_peaks"][0],press_peaks))[5:]
        self.bme_688_data["co2_peaks"][0]   = np.sort(np.append(self.bme_688_data["co2_peaks"][0],co2_peaks))[5:]

    def get_BMI270_data(self):
        return self.bmi_270_data
    
    def get_BME688_data(self):
        return self.bme_688_data

    def decode_n_save(self, data):
        self.cache += data
        if b'<' not in self.cache or b'>' not in self.cache:
            return
        try:
            self.decode_channel[self.sensor](self.cache)
        except : pass
        self.cache = b''

    def wait(self):
        self.sem.acquire()
    
    def go(self):
        self.sem.release()

    def sem_status(self):
        return self.sem._value

    def send_message(self, data:str):
        data = (data+'\0').encode()
        msg = pack(f'{len(data)}s', data)
        self.serial.write(msg)
        print("--> ",data)

    def readline(self):
        msg = self.serial.readline()
        try:
            return msg.decode().strip()
        except serial.serialutil.SerialException as e:
            self.sensor = None
            raise e
        except:
            with open('errors.log', 'a') as f:
                f.write(f"[DECODE ERROR] - {msg}\n")

def convert_value_data(l, type = int):
    try:
        l = [type(i) for i in l]
    except Exception as e:
        print(l)
        with open("error.log", "a") as f:
            f.write(str(l))
            
        # import traceback
        # traceback.print_exc()
    return np.array(l)

def convert_complex_data(l):
    # [ftax, ftay, ..., ftgy, ftgz] = l
    for i, dim  in enumerate(l):
        # 'val1-val2-...-valn' = dim
        dim = dim.split(';')
        for j, val in enumerate(dim):
            # 'real,imag' = val
            real, imag = val.split(',')
            dim[j] = complex(float(real), float(imag))
        l[i] = dim

    return l