import serial
from struct import pack, unpack

COM_PORT = '/dev/ttyUSB1'  # Replace with your COM port
BAUD_RATE = 115200  # Match the baud rate used by your ESP32s2

ser = serial.Serial(COM_PORT, BAUD_RATE, timeout = 1)

# Functions 
def send_message(message):
    ser.write(message)

def change_powermode():
    while True:
        print(""" ============ Powermode ============ 
                \r  1. Low power
                \r  2. Normal power
                \r  3. Performance power
                \r  4. Suspend
                \r  q. Quit""")
        option = input("--> ").lower().strip()
        if option == 'q':
            return  
        if not ('0' < option < '5'):
            print("Invalid option")
            continue
        option = 'PWR#' + option + '\0'
        message = pack('6s', option.encode())
        send_message(message)
        return message

def display_odr_choices(options:dict, sensor:str):
    print(f"New {sensor} ODR:")
    for key, value in options.items():
        print(f"  {key}. {value}")
    print("  q. Quit")

def change_acc_odr(options:dict, choices: dict):
    while True:
        display_odr_choices(options, 'Accelerometer')
        option = input("--> ").lower().strip()
        if option == 'q':
            return
        if option not in options.keys():
            print("Invalid option")
            continue
        choices['acc'] = option
        return

def change_gyr_odr(options:dict, choices: dict):
    while True:
        display_odr_choices(options, 'Gyroscope')
        option = input("--> ").lower().strip()
        if option == 'q':
            return
        if option not in options.keys():
            print("Invalid option")
            continue
        option = str(hex(int(option) + 5)[2:])
        choices['gyr'] = option
        return
    

def change_sampling_rate(choices: dict):
    acc_options = {'1': '25/32', '2': '25/16',
                    '3': '25/8', '4': '25/4',
                    '5': '25/2', '6': '25',
                    '7': '50', '8': '100',
                    '9': '200', '10': '400',
                    '11': '800', '12': '1600', 
                }
    gyr_options ={'1': '25', '2': '50',
                    '3': '100', '4': '200',
                    '5': '400', '6': '800',
                    '7': '1600', '8': '3200'}
    while True:
        acc = choices.get('acc', None)
        gyr = choices.get('gyr', None)
        gyr = str(int(gyr, 16) - 5) if gyr else None
        print(f""" ============ Sampling rate Menu ============
                \r  1. Change Accelerometer ODR - Current: {(acc_options[acc] + ' Hz') if acc else 'Default'}
                \r  2. Change Gyroscope ODR - Current: {((gyr_options[gyr]) + ' Hz') if gyr else 'Default'}
                \r  q. Quit
                \r  [ENTER] confirm changes""")
        option = input("--> ")
        option = option.strip()
        match option:
            case 'q':
                return
            case '1':
                change_acc_odr(acc_options, choices)
            case '2':
                change_gyr_odr(gyr_options, choices)
            case '':
                break
            case default:
                print("Invalid option")
    command = 'ODR'
    acc = choices.get('acc', None)
    gyr = choices.get('gyr', None)
    command += f'#{acc if acc else "0"}'
    command += f'#{gyr if gyr else "0"}'
    if command == 'ODR#0#0':
        print("No changes made")
        return
    command += '\0'
    message = pack(f'{len(command)}s', command.encode())
    send_message(message)
    return message


def interface():
    odr = {'acc':None, 'gyr':None}
    while True:
        print(""" ============ ESP32 Monitor ============ 
                \r  1. Change powermode
                \r  2. Change sampling rate""")
        option = input("--> ").lower().strip()
        rc = ''
        match option:
            case '1':
                rc = change_powermode()
            case '2':
                rc = change_sampling_rate(odr)
            case 'q':
                return
            case default:
                print("Invalid option")
                continue
        if rc:
            print(rc)
            
