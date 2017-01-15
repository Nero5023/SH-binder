from twisted.internet import reactor, protocol

class Echo(protocol.Protocol):
    """docstring for Echo"""

    def dataReceived(self, data):
        print(data)
        self.transport.write(data)

def main():
    factory = protocol.ServerFactory()
    factory.protocol = Echo
    reactor.listenTCP(8000, factory)
    reactor.run()

if __name__ == '__main__':
    main()