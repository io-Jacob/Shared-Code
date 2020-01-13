from __future__ import absolute_import
from __future__ import print_function, unicode_literals

import codecs
import os
import sys
import threading
import glob
import time

import esptool

import serial

from serial.tools.list_ports import comports
from serial.tools import hexlify_codec


from pprint import pprint
import urllib.request


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






port_array = {}
device_array = {}

input('Press enter when only the Fixture Input is connected')

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

# transmitter_board = serial.Serial(device_array.get('transmitter'), 115200, timeout=1000, rtscts=False, dsrdtr=False)
transmitter_board = serial.Serial()
transmitter_board.baudrate = 115200
transmitter_board.port = device_array.get('transmitter')
transmitter_board.timeout = 1000
transmitter_board.rts = False
transmitter_board.dtr = False
print(transmitter_board)

transmitter_board.open()

print('er')
time.sleep(20)
print(transmitter_board.rts)
print(transmitter_board.dtr)
print(transmitter_board.rtscts)
print(transmitter_board.dsrdtr)

print('bout to start readin')
print(time.time())
cFlag = True
while cFlag:
    print('start cycle')
    time.sleep(20)
    # read = transmitter_board.read_until('{')
    read = transmitter_board.read(128)
    print(read)
    input('---Pause')
    if(len(read)):
        print(time.time())




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

print('Firmware Choices:')
for firmware in firmware_choices:
    print('['+firmware+']: ' + firmware_choices.get(firmware).get('name'))
print('')
firmware_choice = input('Please enter the number of the desired firmware: ')

firmware = firmware_choices.get(firmware_choice)

print(firmware.get('transmitter').get('firmware'))
transmitter_firmware_file = urllib.request.urlretrieve(str(firmware.get('transmitter').get('firmware')), './transmitter_firmware.bin')
print(transmitter_firmware_file)

print(firmware.get('transmitter').get('spiffs'))
transmitter_spiffs_file = urllib.request.urlretrieve(str(firmware.get('transmitter').get('spiffs')), './transmitter_spiffs.bin')
print(transmitter_spiffs_file)

print(firmware.get('transmitter').get('bootloader'))
transmitter_bootloader_file = urllib.request.urlretrieve(str(firmware.get('transmitter').get('bootloader')), './transmitter_bootloader.bin')
print(transmitter_bootloader_file)

print(firmware.get('transmitter').get('partitions'))
transmitter_partitions_file = urllib.request.urlretrieve(str(firmware.get('transmitter').get('partitions')), './transmitter_partitions.bin')
print(transmitter_partitions_file)


print('')
print('fingers crossed:')

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
print('fingers crossed:')

# try:
espmodule = esptool.main(['--chip', 'esp32', '--port', device_array.get('receiver'), '--baud', '921600', '--before', 'default_reset', '--after', 'hard_reset', 'write_flash', '-z', '--flash_mode', 'dio', '--flash_freq', '40m', '--flash_size', 'detect', '0x1000', 'receiver_bootloader.bin', '0x8000', 'receiver_partitions.bin', '0x00290000', 'receiver_spiffs.bin', '0x10000', 'receiver_firmware.bin'])
