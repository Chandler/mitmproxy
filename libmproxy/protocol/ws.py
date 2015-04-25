from __future__ import absolute_import
import select
import socket
from .primitives import ProtocolHandler, Flow
from netlib.utils import cleanBin
from netlib.tcp import NetLibError
from . import http
from netlib import websockets

class WebSocketsConnectionFlow(Flow):
    """
        A type of flow which enacapsulates a single WebSockets connection
        and optionally contains a list of any frames that have been passed over this connection
    """
    def __init__(self, client_conn, server_conn, live = None):
        super(WebSocketsConnectionFlow, self).__init__("ws", client_conn, server_conn, live)
        
        self.clientHandshake = None
        """@type: http.HTTPRequest"""
        
        self.serverHandshake = None        
        """@type: http.HTTPResponse"""
      
        self.frames = []
        """@type: [WebSocketsFrame]"""

        _stateobject_attributes = Flow._stateobject_attributes.copy()
        _stateobject_attributes.update(
            clientHandshake=http.HTTPRequest,
            serverHandshake=http.HTTPResponse
        )


class WSFrame(object):
    """
        enacapsulates a single WebSockets frame
        optionally contains a reference to WebSocketsConnectionFlow corresponding
        to the connection this frame was sent over. 
    """
    def __init__(self, frame, ws_connection_flow = None):
        super(WebSocketsFrameFlow, self).__init__(
            "ws",
            ws_connection_flow.client_conn,
            ws_connection_flow.server_conn,
            ws_connection_flow.live
        )
        self.parent_flow = ws_connection_flow
        """@type: WebSocketsConnectionFlow"""

        self.frame = frame
        """@type: WebSocketsFrame"""

class WebSocketsHandler(ProtocolHandler):
    chunk_size = 4096

    def __init__(self, c):
        super(WebSocketsHandler, self).__init__(c)
    
    def handle_messages(self):
        self.c.establish_server_connection()

        server = "%s:%s" % self.c.server_conn.address()[:2]

        buf = memoryview(bytearray(self.chunk_size))

        conns = [self.c.client_conn.rfile, self.c.server_conn.rfile]

        conn_flow = WebSocketsConnectionFlow(self.c.client_conn, self.c.server_conn, self.live)

        try:
            while True:
                r, _, _ = select.select(conns, [], [], 10)
                for rfile in r:
                    if self.c.client_conn.rfile == rfile:
                        src, dst = self.c.client_conn, self.c.server_conn
                        direction = "->"
                        src_str, dst_str = "client", "server"
                    else:
                        dst, src = self.c.client_conn, self.c.server_conn
                        direction = "<-"
                        dst_str, src_str = "client", "server"

                    closed = False

                    size = src.connection.recv_into(buf)
                    if not size:
                        closed = True

                    if closed:
                        conns.remove(src.rfile)
                        dst.connection.shutdown(socket.SHUT_WR)

                        if len(conns) == 0:
                            return
                        continue
 
                    mitmdump_output = "WebSockets frame"
              
                    self.c.log(mitmdump_output, "info")

                    # take the bytes and construct a websockets frame and frame_flow
                    frame_bytes = buf[:size].tobytes()

                    # try:
                    frame       = websockets.Frame.from_bytes(frame_bytes)
                    frame_flow  = WSFrame(frame, conn_flow)
                    self.c.log(frame.human_readable(), "info")

                    # send flows to flowmaster
                    self.c.channel.tell("websockets_connection", conn_flow)
                    self.c.channel.tell("websockets_frame", frame_flow)
                    # except:
                    #     return

                    # pass bytes onto their destination regardless of if we were able to parse them
                    dst.connection.send(buf[:size])
        except (socket.error, NetLibError) as e:
            self.c.log("TCP connection closed unexpectedly.", "debug")
            return


