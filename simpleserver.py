from twisted.internet import reactor
from twisted.internet.protocol import Protocol, Factory
from LightSensor import LightSensor
import json

PORT = 8000

class Echo(Protocol):
    """docstring for Echo"""


    def connectionMade(self):
        print("Got connection from", self.transport.client)

    def connectionLost(self, reason):
        print(self.transport.client, 'disconnected')

    def dataReceived(self, data):
        print(data)
        data = data.decode(encoding='UTF-8')
        jsonData = json.loads(data)
        result = {'result': 'success'};
        if jsonData['target'] == "LightSensor":
            result['value'] = LightSensor().getCurrentLightStatus()
        # self.factory.send("%s" % (data))
        # replay = "%s" % (data.decode(encoding='UTF-8')) 
        replay = json.dumps(result)
        replay = bytes(replay, 'utf-8')
        self.transport.write(replay)

def main():
    print("ServerStarting")
    factory = Factory()
    factory.protocol = Echo
    reactor.listenTCP(PORT, factory)
    reactor.run()

if __name__ == '__main__':
    main()