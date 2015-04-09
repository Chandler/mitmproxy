def protocol_handler(protocol):
    """
    @type protocol: str
    @returns: libmproxy.protocol.primitives.ProtocolHandler
    """
    import http, tcp, ws

    protocols = {
      'http':      dict(handler=http.HTTPHandler, flow=http.HTTPFlow),
      'tcp':       dict(handler=tcp.TCPHandler),
      'websocket': dict(handler=ws.WebSocketsHandler)
    }
    
    if protocol in protocols:
        return protocols[protocol]["handler"]

    raise NotImplementedError("Unknown Protocol: %s" % protocol)   # pragma: nocover
