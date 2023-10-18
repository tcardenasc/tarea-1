import serial
from struct import pack, unpack

# Set the COM port and baud rate
COM_PORT = '/dev/ttyUSB0'  # Replace with your COM port
BAUD_RATE = 115200  # Match the baud rate used by your ESP32s2

# Open the serial connection
ser = serial.Serial(COM_PORT, BAUD_RATE, timeout = 1)

# Functions 
def send_message(message):
    ser.write(message)

def receive_response():
    response = ser.readline()  # Reading until \0
    return response

def receive_data():
    data = receive_response()
    data = unpack("fff", data)
    print(f'Received: {data}')
    return data

def send_end_message():
    end_message = pack('4s', 'END\0'.encode())
    ser.write(end_message)

# Send "BEGIN" message
message = pack('6s','BEGIN\0'.encode())
ser.write(message)

# Read data from the serial port, waiting for the data
counter = 0
while True:
    if ser.in_waiting > 0:
        try:
            message = receive_data()
        except:
            print('Error en leer mensaje')
            continue
        else: 
            counter += 1
            print(counter)
        finally:
            if counter == 10:
                print('Lecturas listas!')
                break


# Sending message to end data sending
send_end_message()

ser.close()
        