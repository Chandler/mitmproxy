from __future__ import absolute_import
import select
import socket
from .primitives import ProtocolHandler
from netlib.utils import cleanBin
from netlib.tcp import NetLibError

class WebSocketsHandler(ProtocolHandler):
    chunk_size = 4096

    def __init__(self, c):
        super(WebSocketsHandler, self).__init__(c)
    
    def handle_messages(self):
        self.c.establish_server_connection()

        server = "%s:%s" % self.c.server_conn.address()[:2]

        buf = memoryview(bytearray(self.chunk_size))

        conns = [self.c.client_conn.rfile, self.c.server_conn.rfile]

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
 
                    mitmdump_output = "Websockets frame"
              
                    self.c.log(mitmdump_output, "info")

                    dst.connection.send(buf[:size])

        except (socket.error, NetLibError) as e:
            self.c.log("TCP connection closed unexpectedly.", "debug")
            return
