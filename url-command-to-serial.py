import serial
import time
import re


commandURI = "http://192.168.1.12/cgibin/runcommand.sh?rndvar:cmd=254,109,1r1t300:cmd=254,110,1r1t300:cmd=254,101,1r1t300"

# split the string using colon (:) as the delimiter and then remove the first two items.
commandList = commandURI.split(':')[2:]

# open the serial port
serialPort = serial.Serial('/dev/tty.usbserial-AC009W0R', baudrate=115200, bytesize=8, stopbits=1, timeout=.5)

returnData = ""
for command in commandList:
    # regex down to the command bytes to send, split into array by commas
    commandData = re.search("cmd=(.*)r", command).group(1).split(',')
    print("Line 18: " + str(commandData))

    # regex down to the number of bytes to expect back, convert into integer
    returnBytes = int(re.search("r(.*)t", command).group(1))
    print("Line 22: " + str(returnBytes))

    #regex down to the timeout on the command, convert into integer
    timeout = int(re.search("t(.*)$", command).group(1))
    print("Line 26: " + str(timeout))

    # convert array from string to int
    for i in range(0, len(commandData)):
        commandData[i] = int(commandData[i])

    # write command to serial port
    serialPort.write(bytearray(commandData))

    # set start time for timeout purposes
    startTime = time.time() * 1000
    readBuffer = bytearray()

    # run loop to read serial port until the number of expected back are returned or timeout is reached
    while startTime > (time.time()*1000-timeout) and len(readBuffer) != returnBytes:
        readBuffer.append(serialPort.read(returnBytes))
        # read = serialPort.read(returnBytes)
        # if len(read):
        #     readBuffer.append(read)

    # return complete at beginning if command succeeded, return e_serial_timeout if failed
    if len(readBuffer) == returnBytes:
        byteString = "complete:"
    else:
        byteString = "e_serial_timeout:"

    # add comma delimiter to individual bytes
    for i in range(0, len(readBuffer)):
        byteString += str(readBuffer[i]) + ","

    # add it to data to be returned, remove trailing comma (,)
    returnData += byteString[:-1]+"\n"

print("Line 59 - Response Data: \n"+returnData)
serialPort.close()
# this is strictly to pause the script after reading
input('')
