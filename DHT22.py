import RPi.GPIO as GPIO
from time import sleep
from Singleton import Singleton

DHT_MAXCOUNT = 32000
DHT_PULSES = 41

class DHT22(metaclass=Singleton):
    """docstring for DHT22"""
    def __init__(self, channel):
        self.channel = channel
        GPIO.setmode(GPIO.BOARD)

    def readData(self):
        # Store the count that each DHT bit pulse is low and high.
        pulseCounts = [0]*(DHT_PULSES*2)
        # set pin to output
        GPIO.setup(self.channel, GPIO.OUT)

        # Set hight for 500 ms
        GPIO.output(self.channel, GPIO.HIGH)
        sleep(0.5)

        # Set pin low for 20 ms
        GPIO.output(self.channel, GPIO.LOW)
        sleep(0.02)

        # set pin to input
        GPIO.setup(self.channel, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        # a very shot delay to read pins
        for x in range(0,50):
            pass

        # Wait for DHT to pull pin low.
        count = 0
        while (GPIO.input(self.channel)):
            if count >= DHT_MAXCOUNT:
                return None
            count += 1

        # Record pulse widths for the expected result bits.
        for i in range(0, DHT_PULSES*2, 2):
            # count how long pi is low and store in pulseCounts[i]
            while (not (GPIO.input(self.channel))):
                pulseCounts[i] += 1
                if pulseCounts[i] >= DHT_MAXCOUNT:
                    return None
            # Count how long pin is high and store in pulseCounts[i+1]
            while (GPIO.input(self.channel)):
                pulseCounts[i+1] += 1
                if pulseCounts[i+1] >= DHT_MAXCOUNT:
                    return None

        # Compute the average low pulse width to use as a 50 microsecond reference threshold.
        # Ignore the first two readings because they are a constant 80 microsecond pulse.
        threshold = 0
        for i in range(2, DHT_PULSES*2, 2):
            threshold += pulseCounts[i]
        threshold = threshold/(DHT_PULSES-1)

        # Interpret each high pulse as a 0 or 1 by comparing it to the 50us reference.
        # If the count is less than 50us it must be a ~28us 0 pulse, and if it's higher then it must be a ~70us 1 pulse.

        data = [0]*5
        for i in range(3, DHT_PULSES*2, 2):
            index = int((i-3)/16)
            data[index] <<= 1
            if pulseCounts[i] >= threshold:
                data[index] |= 1

        print("Data: 0x%x 0x%x 0x%x 0x%x 0x%x\n" %(data[0], data[1], data[2], data[3], data[4]))

        result = {}
        checkSum = ((data[0] + data[1] + data[2] + data[3]) & 0xFF)
        if data[4] == checkSum:
            result["humidity"] = (data[0] * 256 + data[1]) / 10.0
            result["temperature"] = ((data[2] & 0x7F) * 256 + data[3]) / 10.0
            if data[2] & 0x80:
                result["temperature"] *= -1
            return result
        else:
            return None

class DHT22Stable(metaclass=Singleton):
    """docstring for DHT22Stable"""

    def __init__(self, gpioPortNum):
        import Adafruit_DHT as dht
        self.gpioPortNum = gpioPortNum

    def readData(self):
        h,t = dht.read_retry(dht.DHT22, self.gpioPortNum)
        result = {}
        result["humidity"] = h
        result["temperature"] = t
        return result
        

if __name__ == '__main__':
    sensor = DHT22(15)
    while True:
        data = sensor.readData()
        print(data)
        sleep(2.5)

