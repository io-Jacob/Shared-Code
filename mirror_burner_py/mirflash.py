from __future__ import absolute_import
from __future__ import print_function, unicode_literals

import codecs
import os
import sys
import threading
import glob
import time
import json

import esptool

import serial

from serial.tools.list_ports import comports
from serial.tools import hexlify_codec


from pprint import pprint
import urllib.request

flash = False
scanFixture = False
scanTransmitter = False
scanReceiver = False

def serial_ports():
    """ Lists serial port names

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
    """
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/cu[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/cu.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.rts = False
            s.dtr = False
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result

def flashFirmware(answers):
    print("Port: "+answers['port'])
    print("Firmware: "+answers['firmware'])

device_array = {"fixture":"/dev/cu.SLAB_USBtoUART", "transmitter":"/dev/cu.SLAB_USBtoUART88", "receiver":"/dev/cu.SLAB_USBtoUART91"}

if scanFixture:
    input('Press enter when only the Fixture Input is connected')

    port_array = {}

    cflag = True
    while cflag:
        print('Scanning for Serial Ports')
        print('Please wait for the scan to complete')

        for serial_port in serial_ports():
            if 'cu.SLAB' in serial_port:
                sp_key = len(port_array)+1
                port_array.update({str(sp_key): serial_port})

        if len(port_array) > 1:
            print('')
            print('---ERROR---')
            print('Too many ESP32 modules are connected')
            input('press enter when only the transmitter is connected')
            port_array = {}
        elif len(port_array) < 1:
            print('')
            print('---ERROR---')
            print('No ESP32 detected. Check that the transmitter is connected or if the ESP32 is functional')
            input('press enter when only the transmitter is connected')
            port_array = {}
        else:
            cflag = False
    device_array.update({'fixture': port_array.get('1')})

if scanTransmitter:
    input('Press enter when the Mirror Transmitter is connected via USB.')

    port_array = {}

    cflag = True
    while cflag:
        print('Scanning for Serial Ports')
        print('Please wait for the scan to complete')

        for serial_port in serial_ports():
            if 'cu.SLAB' in serial_port and serial_port != device_array.get('fixture'):
                sp_key = len(port_array)+1
                port_array.update({str(sp_key): serial_port})

        if len(port_array) > 1:
            print('')
            print('---ERROR---')
            print('Too many ESP32 modules are connected')
            input('press enter when only the transmitter is connected')
            port_array = {}
        elif len(port_array) < 1:
            print('')
            print('---ERROR---')
            print('No ESP32 detected. Check that the transmitter is connected or if the ESP32 is functional')
            input('press enter when only the transmitter is connected')
            port_array = {}
        else:
            cflag = False
    device_array.update({'transmitter': port_array.get('1')})

if scanReceiver:
    input('Press enter when the Mirror Receiver is connected via USB.')

    port_array = {}

    cflag = True
    while cflag:
        print('Scanning for Serial Ports')
        print('Please wait for the scan to complete')

        for serial_port in serial_ports():
            if 'cu.SLAB' in serial_port and serial_port != device_array.get('fixture') and serial_port != device_array.get('transmitter'):
                sp_key = len(port_array)+1
                port_array.update({str(sp_key): serial_port})

        if len(port_array) > 1:
            print('')
            print('---ERROR---')
            print('Too many ESP32 modules are connected')
            input('press enter when only the transmitter is connected')
            port_array = {}
        elif len(port_array) < 1:
            print('')
            print('---ERROR---')
            print('No ESP32 detected. Check that the transmitter is connected or if the ESP32 is functional')
            input('press enter when only the transmitter is connected')
            port_array = {}
        else:
            cflag = False
    device_array.update({'receiver': port_array.get('1')})

print(device_array)

firmware_choices = {
    '1': {
        'name': '4-20 mA Mirror -- 1-Channel',
        'transmitter': {
            'firmware': '/firmware.bin',
            'spiffs': '/spiffs.bin',
            'bootloader': '/bootloader.bin',
            'partitions': '/partitions.bin'
        },
        'receiver': {
            'firmware': '/firmware.bin',
            'spiffs': '/spiffs.bin',
            'bootloader': '/bootloader.bin',
            'partitions': '/partitions.bin'
        }
    },
    '2': {
        'name': '4-20 mA Mirror -- 2-Channel',
        'transmitter': {
            'firmware': '/firmware.bin',
            'spiffs': '/spiffs.bin',
            'bootloader': '/bootloader.bin',
            'partitions': '/partitions.bin'
        },
        'receiver': {
            'firmware': '/firmware.bin',
            'spiffs': '/spiffs.bin',
            'bootloader': '/bootloader.bin',
            'partitions': '/partitions.bin'
        }
    },
    '3': {
        'name': '4-20 mA Mirror -- 4-Channel',
        'transmitter': {
            'firmware': 'https://ncd-esp32.s3.amazonaws.com/4-20_Input_Mirror_Transmitter_4_Channel/firmware.bin',
            'spiffs': 'https://ncd-esp32.s3.amazonaws.com/4-20_Input_Mirror_Transmitter_4_Channel/spiffs.bin',
            'bootloader': 'https://ncd-esp32.s3.amazonaws.com/4-20_Input_Mirror_Transmitter_4_Channel/bootloader.bin',
            'partitions': 'https://ncd-esp32.s3.amazonaws.com/4-20_Input_Mirror_Transmitter_4_Channel/partitions.bin'
        },
        'receiver': {
            'firmware': 'https://ncd-esp32.s3.amazonaws.com/4-20_Output_Mirror_Transmitter_4_Channel/firmware.bin',
            'spiffs': 'https://ncd-esp32.s3.amazonaws.com/4-20_Output_Mirror_Transmitter_4_Channel/spiffs.bin',
            'bootloader': 'https://ncd-esp32.s3.amazonaws.com/4-20_Output_Mirror_Transmitter_4_Channel/bootloader.bin',
            'partitions': 'https://ncd-esp32.s3.amazonaws.com/4-20_Output_Mirror_Transmitter_4_Channel/partitions.bin'
        }
    },
    '4': {
        'name': '4-20 mA Mirror -- 8-Channel',
        'transmitter': {
            'firmware': '/firmware.bin',
            'spiffs': '/spiffs.bin',
            'bootloader': '/bootloader.bin',
            'partitions': '/partitions.bin'
        },
        'receiver': {
            'firmware': '/firmware.bin',
            'spiffs': '/spiffs.bin',
            'bootloader': '/bootloader.bin',
            'partitions': '/partitions.bin'
        }
    },
    # '5': {
    #     'name': '0-10 V Mirror 1-Channel',
    #     'firmware': 'https://ncd-esp32.s3.amazonaws.com/Mega_Modem/firmware.bin',
    #     'spiffs': 'https://ncd-esp32.s3.amazonaws.com/Mega_Modem/spiffs.bin',
    #     'bootloader': 'https://ncd-esp32.s3.amazonaws.com/Mega_Modem/bootloader.bin',
    #     'partitions': 'https://ncd-esp32.s3.amazonaws.com/Mega_Modem/partitions.bin'
    # },
    # '6': {
    #     'name': '0-10 V Mirror 2-Channel',
    #     'firmware': 'https://ncd-esp32.s3.amazonaws.com/Cellular_MQTT/firmware.bin',
    #     'spiffs': 'https://ncd-esp32.s3.amazonaws.com/Cellular_MQTT/spiffs.bin',
    #     'bootloader': 'https://ncd-esp32.s3.amazonaws.com/Cellular_MQTT/bootloader.bin',
    #     'partitions': 'https://ncd-esp32.s3.amazonaws.com/Cellular_MQTT/partitions.bin'
    # }
}

if flash:
    print('Firmware Choices:')
    for firmware in firmware_choices:
        print('['+firmware+']: ' + firmware_choices.get(firmware).get('name'))
    print('')
    firmware_choice = input('Please enter the number of the desired firmware: ')

    firmware = firmware_choices.get(firmware_choice)

    # print(firmware.get('transmitter').get('firmware'))
    transmitter_firmware_file = urllib.request.urlretrieve(str(firmware.get('transmitter').get('firmware')), './transmitter_firmware.bin')
    # print(transmitter_firmware_file)

    # print(firmware.get('transmitter').get('spiffs'))
    transmitter_spiffs_file = urllib.request.urlretrieve(str(firmware.get('transmitter').get('spiffs')), './transmitter_spiffs.bin')
    # print(transmitter_spiffs_file)

    # print(firmware.get('transmitter').get('bootloader'))
    transmitter_bootloader_file = urllib.request.urlretrieve(str(firmware.get('transmitter').get('bootloader')), './transmitter_bootloader.bin')
    # print(transmitter_bootloader_file)

    # print(firmware.get('transmitter').get('partitions'))
    transmitter_partitions_file = urllib.request.urlretrieve(str(firmware.get('transmitter').get('partitions')), './transmitter_partitions.bin')
    # print(transmitter_partitions_file)


    print('')
    print('Flashing Transmitter')

    # try:
    espmodule = esptool.main(['--chip', 'esp32', '--port', device_array.get('transmitter'), '--baud', '921600', '--before', 'default_reset', '--after', 'hard_reset', 'write_flash', '-z', '--flash_mode', 'dio', '--flash_freq', '40m', '--flash_size', 'detect', '0x1000', 'transmitter_bootloader.bin', '0x8000', 'transmitter_partitions.bin', '0x00290000', 'transmitter_spiffs.bin', '0x10000', 'transmitter_firmware.bin'])
        # espmodule = esptool.main(['--chip', 'esp32', '--port', '/dev/cu.SLAB_USBtoUART', '--baud', '921600', '--before', 'default_reset', '--after', 'hard_reset', 'write_flash', '-z', '--flash_mode', 'dio', '--flash_size', 'detect', '2691072', 'spiffs.bin', '0x10000', 'firmware.bin'])
    # except:
        # print('fail cu')

    print(firmware.get('receiver').get('firmware'))
    receiver_firmware_file = urllib.request.urlretrieve(str(firmware.get('receiver').get('firmware')), './receiver_firmware.bin')
    print(receiver_firmware_file)

    print(firmware.get('receiver').get('spiffs'))
    receiver_spiffs_file = urllib.request.urlretrieve(str(firmware.get('receiver').get('spiffs')), './receiver_spiffs.bin')
    print(receiver_spiffs_file)

    print(firmware.get('receiver').get('bootloader'))
    receiver_bootloader_file = urllib.request.urlretrieve(str(firmware.get('receiver').get('bootloader')), './receiver_bootloader.bin')
    print(receiver_bootloader_file)

    print(firmware.get('receiver').get('partitions'))
    receiver_partitions_file = urllib.request.urlretrieve(str(firmware.get('receiver').get('partitions')), './receiver_partitions.bin')
    print(receiver_partitions_file)


    print('')
    print('Flashing Receiver:')

    # try:
    espmodule = esptool.main(['--chip', 'esp32', '--port', device_array.get('receiver'), '--baud', '921600', '--before', 'default_reset', '--after', 'hard_reset', 'write_flash', '-z', '--flash_mode', 'dio', '--flash_freq', '40m', '--flash_size', 'detect', '0x1000', 'receiver_bootloader.bin', '0x8000', 'receiver_partitions.bin', '0x00290000', 'receiver_spiffs.bin', '0x10000', 'receiver_firmware.bin'])

transmitter_config = json.loads('{}')

fixture_readings = json.loads('{}')

receiver_config = json.loads('{}')

transmitter_board = serial.Serial()
transmitter_board.baudrate = 115200
transmitter_board.port = device_array.get('transmitter')
transmitter_board.timeout = 1000
transmitter_board.rts = False
transmitter_board.dtr = False

receiver_board = serial.Serial()
receiver_board.baudrate = 115200
receiver_board.port = device_array.get('receiver')
receiver_board.timeout = 1000
receiver_board.rts = False
receiver_board.dtr = False

fixture_board = serial.Serial()
fixture_board.baudrate = 115200
fixture_board.port = device_array.get('fixture')
fixture_board.timeout = 1000
fixture_board.rts = False
fixture_board.dtr = False

def loadTransmitterConfig(destinationPort):
    if not destinationPort.is_open:
        try:
            destinationPort.open()
        except:
            sys.exit("Failed to open port to Transmitter board")

    print('Loading Transmitter Configuration')
    timeout = time.time()+30
    while time.time() < timeout:
        try:
            receivedByteArray = destinationPort.read_until("\r\n".encode('utf-8'))
            received_line = receivedByteArray.decode("utf-8")
            received_line = received_line.replace('\r\n','')
            transmitter_json = json.loads(received_line)
            if 'local_address' in transmitter_json and 'channel_1' in transmitter_json and 'channel_2' in transmitter_json and 'channel_3' in transmitter_json and 'channel_4' in transmitter_json:

                if 'raw' in transmitter_json['channel_1'] and 'raw' in transmitter_json['channel_2'] and 'raw' in transmitter_json['channel_3'] and 'raw' in transmitter_json['channel_4']:
                    global transmitter_config
                    transmitter_config = transmitter_json
                    destinationPort.close()
                    # print(json.dumps(transmitter_config))
                    print('Transmitter Configuration Loaded:')
                    print("")
                    return
        except:
            continue
    sys.exit("failed to load Transmitter Configuration")

def loadReceiverConfig(destinationPort):
    if not destinationPort.is_open:
        try:
            destinationPort.open()
        except:
            sys.exit("Failed to open port to Receiver board")

    print('Loading Receiver Configuration')
    timeout = time.time()+30
    while time.time() < timeout:
        try:
            receivedByteArray = destinationPort.read_until("\r\n".encode('utf-8'))
            received_line = receivedByteArray.decode("utf-8")
            received_line = received_line.replace('\r\n','')
            receiver_json = json.loads(received_line)
            if 'local_address' in receiver_json and 'channel_1' in receiver_json and 'channel_2' in receiver_json and 'channel_3' in receiver_json and 'channel_4' in receiver_json:
                if 'raw' in receiver_json['channel_1'] and 'raw' in receiver_json['channel_2'] and 'raw' in receiver_json['channel_3'] and 'raw' in receiver_json['channel_4']:
                    global receiver_config
                    receiver_config = receiver_json
                    destinationPort.close()
                    # print(json.dumps(receiver_config))
                    print("Receiver Configuration Loaded:")
                    print("")
                    return
        except:
            continue
    sys.exit("failed to load Receiver Configuration")

def getFixtureReadings(destinationPort):
    if not destinationPort.is_open:
        try:
            destinationPort.open()
        except:
            sys.exit("Failed to open port to Fixture board")

    print('Loading readings from fixture board')
    timeout = time.time()+30
    while time.time() < timeout:
        receivedByteArray = destinationPort.read_until("\r\n".encode('utf-8'))
        received_line = receivedByteArray.decode("utf-8")
        received_line = received_line.replace('\r\n','')
        try:
            fixture_json = json.loads(received_line)
            if 'channel_1' in fixture_json and 'channel_2' in fixture_json and 'channel_3' in fixture_json and 'channel_4' in fixture_json:
                global fixture_readings
                fixture_readings['channel_1'] = fixture_json['channel_1']
                fixture_readings['channel_2'] = fixture_json['channel_2']
                fixture_readings['channel_3'] = fixture_json['channel_3']
                fixture_readings['channel_4'] = fixture_json['channel_4']
                destinationPort.close()
                return
        except:
            continue
    sys.exit("failed to load Receiver Configuration")

def pairDevices(transmitterPort, receiverPort):
    timeout = time.time()+30
    while time.time() < timeout:
            if 'local_address' in transmitter_config and 'local_address' in receiver_config:
                if transmitter_config['local_address'] != 'empty' and receiver_config['local_address'] != 'empty':
                    print("Pairing Devices")
                    try:
                        transmitterDestinationJSON = json.loads('{}')
                        transmitterDestinationJSON['destination_address'] = receiver_config['local_address']
                        if not transmitterPort.is_open:
                            transmitterPort.open()
                            time.sleep(0.1)
                        transmitterPort.write((json.dumps(transmitterDestinationJSON)).encode())
                        transmitterPort.write('\n'.encode())
                        time.sleep(0.5)
                        transmitterPort.close()
                    except:
                        sys.exit('failed to write destination address to transmitter')

                    try:
                        receiverDestinationJSON = json.loads('{}')
                        receiverDestinationJSON['destination_address'] = transmitter_config['local_address']
                        if not receiverPort.is_open:
                            receiverPort.open()
                            time.sleep(0.1)
                        receiverPort.write((json.dumps(receiverDestinationJSON)).encode())
                        receiverPort.write('\n'.encode())
                        time.sleep(0.5)
                        receiverPort.close()
                    except:
                        sys.exit('failed to write destination address to receiver')
                    while time.time() < timeout:
                        loadTransmitterConfig(transmitterPort)
                        if transmitter_config['destination_address'] == receiver_config['local_address']:
                            break
                    while time.time() < timeout:
                        loadReceiverConfig(receiverPort)
                        if receiver_config['destination_address'] == transmitter_config['local_address']:
                            print("pairing complete")
                            break
                    print("Awaiting successful communication")
                    while time.time() < timeout:
                        loadReceiverConfig(receiverPort)
                        if receiver_config["channel_1"]["converted"] > 2 and receiver_config["channel_2"]["converted"] > 2 and receiver_config["channel_3"]["converted"] > 2 and receiver_config["channel_4"]["converted"] > 2:
                            print("Device Communication Successful")
                            return
                        else:
                            print("channel 1 reading: ", end='')
                            print(receiver_config["channel_1"]["converted"])
                    sys.exit("Device Connection Failed")
            if not 'local_address' in transmitter_config:
                print('no local address in transmitter_config:')
                print(json.dumps(transmitter_config))
                loadTransmitterConfig(transmitterPort)
            else:
                if transmitter_config['local_address'] == 'empty':
                    print("local_address in transmitter_config empty")
                    loadTransmitterConfig(transmitterPort)
            if not 'local_address' in receiver_config:
                print('no local address in receiver_config')
                loadReceiverConfig(receiverPort)
            else:
                if receiver_config['local_address'] == 'empty':
                    print("local_address in receiver_config empty")
                    loadReceiverConfig(receiverPort)
    sys.exit("Pairing Timed Out")

def calibrateReceiver(receiverPort, fixturePort):
    print("calibrating receiver")
    timeout = time.time()+30
    while time.time() < timeout:
        getFixtureReadings(fixturePort)
        if 'channel_1' in fixture_readings and 'channel_2' in fixture_readings and 'channel_3' in fixture_readings and 'channel_4' in fixture_readings:
            if fixture_readings['channel_1'] > 2 and fixture_readings['channel_2'] > 2 and fixture_readings['channel_3'] > 2 and fixture_readings['channel_4'] > 2:
                try:
                    receiverConfigJSON = json.loads('{}')
                    receiverConfigJSON['channel_one_calibration'] = fixture_readings['channel_1']/receiver_config['channel_1']['raw']
                    receiverConfigJSON['channel_two_calibration'] = fixture_readings['channel_2']/receiver_config['channel_2']['raw']
                    receiverConfigJSON['channel_three_calibration'] = fixture_readings['channel_3']/receiver_config['channel_3']['raw']
                    receiverConfigJSON['channel_four_calibration'] = fixture_readings['channel_4']/receiver_config['channel_4']['raw']
                    if not receiverPort.is_open:
                        try:
                            receiverPort.open()
                        except:
                            sys.exit("Failed to open port to Receiver board")
                    receiverPort.write((json.dumps(receiverConfigJSON)).encode())
                    receiverPort.write('\n'.encode())
                    receiverPort.close()
                    return
                except:
                    sys.exit("Configuration of Receiver Failed")
    sys.exit("Configuration of Receiver Failed")

def calibrateTransmitter(destinationPort):
    print("Calibrating Transmitter")
    timeout = time.time()+30
    while time.time() < timeout:
        try:
            transmitterConfigJSON = json.loads('{}')
            transmitter_json = json.loads(received_line)
            if 'channel_1' in transmitter_config and 'channel_2' in transmitter_config and 'channel_3' in transmitter_config and 'channel_4' in transmitter_config:

                if 'raw' in transmitter_json['channel_1'] and 'raw' in transmitter_json['channel_2'] and 'raw' in transmitter_json['channel_3'] and 'raw' in transmitter_json['channel_4']:
                    transmitterConfigJSON['channel_one_calibration'] = 12.00/transmitter_config['channel_1']['raw']
                    transmitterConfigJSON['channel_two_calibration'] = 12.00/transmitter_config['channel_2']['raw']
                    transmitterConfigJSON['channel_three_calibration'] = 12.00/transmitter_config['channel_3']['raw']
                    transmitterConfigJSON['channel_four_calibration'] = 12.00/transmitter_config['channel_4']['raw']
                    if not destinationPort.is_open:
                        try:
                            destinationPort.open()
                        except:
                            sys.exit("Failed to open port to Transmitter board")
                    destinationPort.write((json.dumps(transmitterConfigJSON)).encode())
                    destinationPort.write('\n'.encode())
                    destinationPort.close()
                    print("Transmitter Calibrated")
                    return
            loadTransmitterConfig()
        except:
            continue
    sys.exit("Configuration of Transmitter Failed")

loadTransmitterConfig(transmitter_board)
loadReceiverConfig(receiver_board)

pairDevices(transmitter_board, receiver_board)

calibrateReceiver(receiver_board, fixture_board)
calibrateTransmitter(transmitter_board)
system.exit("Finished!")
