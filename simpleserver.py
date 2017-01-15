from twisted.internet import reactor
from twisted.internet.protocol import Protocol, Factory

PORT = 8000

class Echo(Protocol):
    """docstring for Echo"""


    def connectionMade(self):
        print("Got connection from", self.transport.client)

    def connectionLost(self, reason):
        print(self.transport.client, 'disconnected')

    def dataReceived(self, data):
        print(data)
        # self.factory.send("%s" % (data))
        replay = "%s" % (data.decode(encoding='UTF-8'))
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