# import server from netlib
from netlib import tcp
from netlib import test
from netlib import websockets as ws
import struct
import SocketServer
from base64 import b64encode
from hashlib import sha1
from mimetools import Message
from StringIO import StringIO
import os

# import client from 3rd party TODO replace
from websocket import create_connection

class WebSocketsHandler(tcp.BaseHandler): 
    def __init__(self, connection, address, server):
        super(WebSocketsHandler, self).__init__(connection, address, server)

    def handle(self):
       self.handshake()
       self.read_next_message()

    def read_next_message(self):
        decoded = ws.server_read_message(self.rfile.read)
        self.on_message(decoded)

    def send_message(self, message):
        ws.server_send_message(self.wfile.write, message)
        self.wfile.flush()
 
    def handshake(self):
        response = ws.read_handshake(self.rfile.read, 1)

        headers = Message(StringIO(response.split('\r\n', 1)[1]))
        if headers.get("Upgrade", None) != "websocket":
            return
        key = headers['Sec-WebSocket-Key']

        response = ws.create_server_handshake(key)
   
        self.wfile.write(response)
        self.wfile.flush()


class WebSocketsEchoHandler(WebSocketsHandler):
    def on_message(self, message):
        if message is not None:
            self.send_message(message)

class WebSocketsClient(tcp.TCPClient):
    def __init__(self, address, source_address=None):
        super(WebSocketsClient, self).__init__(address, source_address)
        self.version    = "13"
        self.key        = b64encode(os.urandom(16)).decode('utf-8')
        self.resource   = "/"

    def connect(self):
        super(WebSocketsClient, self).connect()

        handshake = ws.create_client_handshake(
              self.address.host,
              self.address.port,
              self.key,
              self.version,
              self.resource
          )

        self.wfile.write(handshake)
        self.wfile.flush()

        response = ws.read_handshake(self.rfile.read, 1)
        
        if not response:
            self.close()

        # TODO validate handshake

    def read_next_message(self):
        try:
            return ws.client_read_message(self.rfile.read)
        except IndexError:
            self.close()
 
    def send_message(self, message):
        ws.client_send_message(self.wfile.write, message, [1,2,3,4])
        self.wfile.flush()

class TestWebSockets(test.ServerTestBase):
    handler = WebSocketsEchoHandler

    def test_basic_websockets_support(self):
        msg    = "hello I'm the client"
        client = WebSocketsClient(("127.0.0.1", self.port))
        client.connect()
        client.send_message(msg)
        response = client.read_next_message()
        print "Assert response: " + str(response)  + "  == message: " + str(msg)
        assert response == msg

    # test multiframe message support

    # test encrypted websockets support

    # test websockets passthrough

    # test websockets frame scripting

    # test websockets frame replay

    # test connection dying

    # test invalid upgrade

    # test 

