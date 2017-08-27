from autobahn.twisted.websocket import WebSocketServerProtocol, \
    WebSocketServerFactory
import json
from LightSensor import LightSensor
from twisted.internet import reactor
from AirQualitySensor import AirQualitySensor
from DHT22 import DHT22Stable as DHT22
from time import sleep
import datetime
import functools
import pymongo

# def sendAirQualityInfo(protocol):
#     sensor = AirQualitySensor()
#     result = {}
#     airQuality = sensor.getAirQuality()
#     if airQuality is None:
#         result = {"result": "fail", "reason": "There is no data"}
#         result = json.dumps(result)
#         result = bytes(result, 'utf8')
#         protocol.sendMessage(result, False)
#     else:
#         result = {"result": "success"}
#         result["data"] = airQuality
#         result = json.dumps(result)
#         result = bytes(result, 'utf8')
#         protocol.sendMessage(result, False)
#     reactor.callLater(3, sendAirQualityInfo, protocol) 

# def sendTemHumInfo(protocol):
#     sensor = DHT22()
#     data = sensor.readData()
#     sleep(2.5)
#     # read twice to get the newest data
#     data = sensor.readData()
#     if data is None:
#         result = {"result": "fail", "reason": "There is no data"}
#         result = json.dump(result)
#         result = bytes(result, 'utf8')
#         protocol.sendMessage(result, False)
#     else:
#         result = {"result": "success"}
#         result["data"] = data
#         result = json.dumps(result)
#         result = bytes(result, 'utf8')
#         protocol.sendMessage(result, False)
#     reactor.callLater(10, sendTemHumInfo, protocol)

def baseSendInfo(data, protocol):
    result = {}
    if data is None:
        result = {"result": "fail", "reason": "There is no data"}
    else:
        result = {"result": "success"}
        result["data"] = data
    result = json.dumps(result)
    result = bytes(result, 'utf8')
    protocol.sendMessage(result, False)


def sendAirQualityInfo(protocol):
    sensor = AirQualitySensor()
    airQuality = sensor.getAirQuality()
    baseSendInfo(airQuality, protocol)
    reactor.callLater(3, sendAirQualityInfo, protocol)

def sendHumInfo(protocol):
    sensor = DHT22()
    data = sensor.readData()
    sleep(2.5)
    # read twice to get the newest data
    data = sensor.readData()
    baseSendInfo(data, protocol)
    reactor.callLater(10, sendHumInfo, protocol)

def sendTemInfo(protocol):
    # DHT22 is Singleton
    sensor = DHT22()
    data = sensor.data
    if data == {}:
        data = None
    baseSendInfo(data, protocol)
    reactor.callLater(10, sendTemInfo, protocol)

def sendAirQualityInfoToDB(timeout, dbCollection):
    sensor = AirQualitySensor()
    airQuality = sensor.getAirQuality()
    if airQuality is not None:
        # utc time
        airQuality["time"] = datetime.datetime.utcnow()
        dbCollection.insert(airQuality)
    cb = functools.partial(sendAirQualityInfoToDB, timeout=timeout, dbCollection=dbCollection)
    reactor.callLater(timeout, cb)

class BinderServerProtocol(WebSocketServerProtocol):
    """docstring for BinderServerProtocol, this is the protocol"""

    def onConnect(self, request):
        print("Client connecting: {0}".format(request.peer))

    def onOpen(self):
        print("WebSocket connecting open.")

    def onMessage(self, payload, isBinary):
        print(type(payload))
        print(isBinary)
        data = ""
        if isBinary:
            print("Binary message received: {0} bytes".format(len(payload)))
            data = payload
        else:
            data = payload.decode('utf8')
            print("Text message received: {0}".format(payload.decode('utf8')))
        jsonData = json.loads(data)
        result = {'result': 'success'};
        if jsonData['target'] == "LightSensor":
            result['value'] = LightSensor().getCurrentLightStatus()
            replay = json.dumps(result)
            replay = bytes(replay, 'utf8')
            self.sendMessage(replay, isBinary)
        elif jsonData['target'] == 'AirQualitySensor':
            sendAirQualityInfo(self)
        elif jsonData['target'] == 'HumSensor':
            sendHumInfo(self)
        elif jsonData['target'] == 'TemSensor':
            sendTemInfo(self)

    def onClose(self, wasClean, code, reason):
        print("WebSocket connection closed: {0}".format(reason))



if __name__ == '__main__':
    import sys

    from twisted.python import log
    

    log.startLogging(sys.stdout)

    factory = WebSocketServerFactory(u"ws://127.0.0.1:9000")
    factory.protocol = BinderServerProtocol

    reactor.listenTCP(9000, factory)

    dbConnection = pymongo.MongoClient(" ", 0)
    sendAirQualityInfoToDB(1, dbConnection.home_status.air_quality)
    reactor.run()