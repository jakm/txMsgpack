
def connect(host, port, timeout=None, reactor=None):
    if reactor is None:
        from twisted.internet import reactor

    from twisted.internet import endpoints
    from txmsgpack.protocol import MsgpackClientFactory

    kwargs = {}

    if timeout is not None:
        kwargs['timeout'] = timeout

    factory = MsgpackClientFactory()

    point = endpoints.TCP4ClientEndpoint(reactor, host, port, **kwargs)
    return point.connect(factory)
