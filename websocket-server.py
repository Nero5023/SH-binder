from autobahn.twisted.websocket import WebSocketServerProtocol, \
    WebSocketServerFactory
import json
from LightSensor import LightSensor
from twisted.internet import reactor
from AirQualitySensor import AirQualitySensor


def sendAirQualityInfo(protocol):
    sensor = AirQualitySensor()
    result = {}
    airQuality = sensor.getAirQuality()
    if airQuality is None:
        result = {"result": "fail", "reason": "There is no data"}
        result = json.dumps(result)
        result = bytes(result, 'utf8')
        protocol.sendMessage(result, False)
    else:
        result = {"result": "success"}
        result["data"] = airQuality
        result = json.dumps(result)
        result = bytes(result, 'utf8')
        protocol.sendMessage(result, False)
    reactor.callLater(3, sendAirQualityInfo, protocol) 


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

    def onClose(self, wasClean, code, reason):
        print("WebSocket connection closed: {0}".format(reason))



if __name__ == '__main__':
    import sys

    from twisted.python import log
    

    log.startLogging(sys.stdout)

    factory = WebSocketServerFactory(u"ws://127.0.0.1:9000")
    factory.protocol = BinderServerProtocol

    reactor.listenTCP(9000, factory)
    reactor.run()