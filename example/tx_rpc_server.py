from twisted.internet import defer, protocol, reactor
from twisted.protocols import memcache
from txmsgpack.server import MsgpackRPCServer

class EchoRPC(MsgpackRPCServer):
    def __init__(self, memcacheClient):
        self.memcacheClient = memcacheClient

    def remote_echo(self, value, msgid=None):
        df = defer.Deferred()
        df.callback(value)
        return df

    def remote_bounce(self, one, two, three):
        if self.memcacheClient is None:
            return self.remote_echo((one, two, three))
        df = self.memcacheClient.set(one, "%s:%s" % (two, three))
        df.addCallback(lambda x:(one, two, three))
        return df

@defer.inlineCallbacks
def main():
    try:
        client = yield (protocol.ClientCreator(reactor, memcache.MemCacheProtocol)
                        .connectTCP("localhost", memcache.DEFAULT_PORT))
    except Exception:
        client = None

    if client is None:
        print "Memcache is not avaiable"
    else:
        print "WARNING: THIS SERVER WILL ADD DATA TO YOUR MEMCACHED SERVICE"
        print "memcache_client: %s" % (client,)

    server = EchoRPC(client)
    server.serve(8007)

if __name__ == '__main__':
    reactor.callWhenRunning(main)
    reactor.run()