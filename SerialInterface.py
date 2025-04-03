import serial
from serial.serialutil import SerialException
import time
import threading
import numpy as np
from datetime import datetime

TYPES_DICT = {
    0x17: 'HCHO',
    0x18: 'VOC',
    0x19: 'CO',
    0x1A: 'CI2',
    0x1B: 'H2',
    0x1C: 'H2S',
    0x1D: 'HCl',
    0x1E: 'HCN',
    0x1F: 'HF',
    0x20: 'NH3',
    0x21: 'NO2',
    0x22: 'O2',
    0x23: 'O3',
    0x24: 'SO2'
}

UNITS_DICT = {
    0x02: 'ppm',

    0x04: 'ppb',
    0x08: '%'
}

GO_PASSIVE = bytearray([0xFF, 0x01, 0x78, 0x41, 0x00, 0x00, 0x00, 0x00, 0x46])
GO_ACTIVE = bytearray([0xFF, 0x01, 0x78, 0x40, 0x00, 0x00, 0x00, 0x00, 0x47])
READ = bytearray([0xFF, 0x00, 0x87, 0x00, 0x00, 0x00, 0x00, 0x00, 0x79])

LED_ON = bytearray([0xFF, 0x01, 0x88, 0x00, 0x00, 0x00, 0x00, 0x00, 0x77])
LED_OFF = bytearray([0xFF, 0x01, 0x89, 0x00, 0x00, 0x00, 0x00, 0x00, 0x77])

MAX_LENGTH = int(1e4)
AVG_LENGTH = int(3)


class SerialInterface:

    def __init__(self, port):
        self.data = np.zeros(MAX_LENGTH)
        self.temp = np.zeros(MAX_LENGTH)
        self.humid = np.zeros(MAX_LENGTH)
        self.times = np.zeros(MAX_LENGTH)
        self.i = 0

        self.ser = serial.Serial(
            port, 9600, bytesize=8, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, timeout=1)

        if ((not self.ser) or (not self.ser.isOpen())):
            raise SerialException("Unable to connect")

        # Blink and switch on the LED
        for i in range(3):
            self.ser.write(LED_ON)
            self.ser.read(2)
            time.sleep(0.1)
            self.ser.write(LED_OFF)
            self.ser.read(2)
            time.sleep(0.1)
        self.ser.write(LED_ON)
        self.ser.read(2)

        # Read sensor type
        self.ser.write(bytearray([0xD1]))
        ss = self.ser.read(9)

        self.decimals = int(int(ss[7] & 0b11110000) / 16)

        self.gas = TYPES_DICT[ss[0]]
        self.maxrange = int(ss[1]) * 256 + int(ss[2])
        self.unit = UNITS_DICT[ss[3]]

        print(
            f"Loaded a sensor for {self.gas} in {self.unit} | range {self.maxrange} {self.unit}, decimals {self.decimals}")

        # Switch off the LED
        self.ser.write(LED_OFF)
        self.ser.read(2)

    def startPooling(self):
        self.ser.flush()
        # self.ser.write(GO_ACTIVE)
        # self.ser.read(2)

        self.keepGoing = True

        self.thread = threading.Thread(target=self.pool_thrd)
        self.thread.start()

    def stopPooling(self):
        self.keepGoing = False
        self.thread.join()

        self.ser.flush()
        # self.ser.write(GO_PASSIVE)
        # self.ser.read(2)

    def pool_thrd(self):
        while self.keepGoing:

            self.ser.write(READ)
            data = self.ser.read(13)

            if (len(data) != 13):
                continue
            self.times[self.i] = datetime.now().timestamp() / 60.0
            self.data[self.i] = (0.0 + int(data[6]) * 256 +
                                 int(data[7])) / (10 ** self.decimals)
            self.temp[self.i] = (0.0 + int(data[8]) * 256 + int(data[9])) / 100.0
            self.humid[self.i] = (0.0 + int(data[10]) * 256 + int(data[11])) / 100.0
            self.i = (self.i + 1) % MAX_LENGTH

            time.sleep(0.1)

    def getLastValue(self, runningMean=True):
        if (runningMean):
            if (self.i > AVG_LENGTH):
                return np.mean(self.data[self.i - AVG_LENGTH: self.i])
            elif (self.i == 0):
                return np.mean(self.data[- AVG_LENGTH:])
            else:
                return np.mean(np.concatenate([self.data[self.i - AVG_LENGTH:], self.data[: self.i]]))

        if (self.i > 0):
            return self.data[self.i - 1]

    def getLastTemp(self, runningMean=True):
        if (runningMean):
            if (self.i > AVG_LENGTH):
                return np.mean(self.temp[self.i - AVG_LENGTH: self.i])
            elif (self.i == 0):
                return np.mean(self.temp[- AVG_LENGTH:])
            else:
                return np.mean(np.concatenate([self.temp[self.i - AVG_LENGTH:], self.temp[: self.i]]))

        if (self.i > 0):
            return self.temp[self.i - 1]

    def getLastHumid(self, runningMean=True):
        if (runningMean):
            if (self.i > AVG_LENGTH):
                return np.mean(self.humid[self.i - AVG_LENGTH: self.i])
            elif (self.i == 0):
                return np.mean(self.humid[- AVG_LENGTH:])
            else:
                return np.mean(np.concatenate([self.humid[self.i - AVG_LENGTH:], self.humid[: self.i]]))

        if (self.i > 0):
            return self.humid[self.i - 1]

    def getAllValues(self):
        if (self.i == 0):
            return self.times, self.data
        
        return np.concatenate([self.times[self.i:], self.times[: self.i]]), np.concatenate([self.data[self.i:], self.data[: self.i]])

    def testPort(port):

        ser = serial.Serial(port, 9600, bytesize=8, parity=serial.PARITY_NONE,
                            stopbits=serial.STOPBITS_ONE, timeout=1)

        if ((not ser) or (not ser.isOpen())):
            return "No Sens connected"

        # Read sensor type
        ser.write(bytearray([0xD1]))
        ss = ser.read(9)

        if (len(ss) != 9):
            return "No Sens connected"

        gas = TYPES_DICT[ss[0]] if ss[0] in TYPES_DICT.keys() else "Unknown"
        maxrange = int(ss[1]) * 256 + int(ss[2])
        unit = UNITS_DICT[ss[3]] if ss[3] in UNITS_DICT.keys() else "Unknown"

        ser.close()

        return f"Sensor for {gas} | range {maxrange} {unit}"
