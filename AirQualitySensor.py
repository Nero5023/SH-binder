import time
import serial
from Singleton import Singleton
SERIAL_PORT = "/dev/ttyS0"

def combineTwoByte(frame, start):
    return (frame[start] << 8) + frame[start+1]

def decode(frame):
    if len(frame) != 32:
        print("The frame's length is not 32 byes! The frame is %s bytes" %(len(frame)))
        return None
    startSymbol0 = frame[0]
    startSymbol1 = frame[1]
    if startSymbol0 != 0x42 or startSymbol1 != 0x4d:
        print("The frame's start symbol is not correct" + str(startSymbol0) + " " + str(startSymbol1))
        return None
    frameLength = combineTwoByte(frame, 2)
    if frameLength != 28:
        print("The frame's length data error, the frameLength data is" + str(frameLength))
        return None
    check_sum_computed = sum(frame[0:30])
    # get low 16 bit
    check_sum_computed = check_sum_computed & 0xffff

    check_sum = combineTwoByte(frame, 30)

    if check_sum != check_sum_computed:
        print("Check sum is not correct")
        return None

    airQuality = {};

    pm1_0_CF = combineTwoByte(frame, 4)
    airQuality["pm1.0_cf"] = pm1_0_CF
    print("PM1_0 (CF=1) %s ug/m3" %(pm1_0_CF))


    pm2_5_CF = combineTwoByte(frame, 6)
    print("PM2.5 (CF=1) %s ug/m3" %(pm2_5_CF))
    airQuality["pm2_5_cf"] = pm2_5_CF

    pm10_CF = combineTwoByte(frame, 8)
    airQuality["pm10_cf"] = pm10_CF
    print("PM10 (CF=1) %s ug/m3" %(pm10_CF))


    pm1_0_atm = combineTwoByte(frame, 10)
    airQuality["pm1_0_atm"] = pm1_0_atm
    print("PM1.0 in the atmosphere %s ug/m3" %(pm1_0_atm))

    pm2_5_atm = combineTwoByte(frame, 12)
    airQuality["pm2_5_atm"] = pm2_5_atm
    print("PM2.5 in the atmosphere %s ug/m3" %(pm2_5_atm))

    pm10_atm = combineTwoByte(frame, 14)
    airQuality["pm10_atm"] = pm10_atm
    print("PM10 in the atmosphere %s ug/m3" %(pm10_atm))

    return airQuality

ser = serial.Serial(SERIAL_PORT, 9600)
ser.inWaiting()

class AirQualitySensor(metaclass=Singleton):
    """AirQualitySensor"""
    def __init__(self):
        self.ser = serial.Serial(SERIAL_PORT, 9600)

    def getAirQuality(self):
        bufferLength = self.ser.inWaiting()
        if bufferLength >= 32:
            effectiveFrame = int(bufferLength/32)
            readLength = effectiveFrame * 32
            print("bufferLength")
            print(bufferLength)
            print("Read length")
            print(readLength)
            data = self.ser.read(readLength)
            print("Start index")
            print((effectiveFrame-1)*32)
            airQuality = decode(data[(effectiveFrame-1)*32:])
            return airQuality
        return None


if __name__ == '__main__':
    sensor = AirQualitySensor()
    # while True:
    #     if sensor.ser.inWaiting() >= 32:
    #         data = sensor.ser.read(32)
    #         decode(data)
    #         print("\n %s"%(sensor.ser.inWaiting()))
    #         print("------------------------")
    #     time.sleep(1)
    while True:
        sensor.getAirQuality()
        print("\n %s"%(sensor.ser.inWaiting()))
        print("------------------------")
        time.sleep(1)
