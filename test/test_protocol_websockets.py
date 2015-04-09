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
    magic = '258EAFA5-E914-47DA-95CA-C5AB0DC85B11'
 
    def __init__(self, connection, address, server):
        super(WebSocketsHandler, self).__init__(connection, address, server)

    def handle(self):
       self.handshake()
       self.read_next_message()
 
    def read_next_message(self):
        length = ord(self.rfile.read(2)[1]) & 127
        if length == 126:
            length = struct.unpack(">H", self.rfile.read(2))[0]
        elif length == 127:
            length = struct.unpack(">Q", self.rfile.read(8))[0]
        masks = [ord(byte) for byte in self.rfile.read(4)]
        decoded = ""
        for char in self.rfile.read(length):
            decoded += chr(ord(char) ^ masks[len(decoded) % 4])
        self.send_message(decoded)


    def send_message(self, message):
        self.wfile.write(chr(129))
        length = len(message)
        if length <= 125:
            self.wfile.write((chr(length)))
        elif length >= 126 and length <= 65535:
            self.wfile.write(chr(126))
            self.wfile.write(struct.pack(">H", length))
        else:
            self.wfile.write(chr(127))
            self.wfile.write(struct.pack(">Q", length))

        self.wfile.write(message)
        self.wfile.flush()
 
    def handshake(self):
        response   = b''
        doubleCLRF = b'\r\n\r\n'
        while True:
            bytes = self.rfile.read(1)
            if not bytes:
                break
            response += bytes
            if doubleCLRF in response:
                break
        data = response

        headers = Message(StringIO(data.split('\r\n', 1)[1]))
        if headers.get("Upgrade", None) != "websocket":
            return
        key = headers['Sec-WebSocket-Key']

        handshake = ws.create_server_handshake(key)

        self.wfile.write(handshake)
        self.wfile.flush()


class WebSocketsEchoHandler(WebSocketsHandler):
    def on_message(self, message):
        if message is not None:
            self.wfile.write(message)
            self.wfile.flush()


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

        response   = b''
        doubleCLRF = b'\r\n\r\n'
        while True:
            bytes = self.rfile.read(1)
            if not bytes:
                break
            response += bytes

            if doubleCLRF in response:
                break

        if not response:
            self.close()

        # TODO validate handshake

    def handshake_request(self):
        headers = [
            ('Host', '%s:%s' % (self.address.host, self.address.port)),
            ('Connection', 'Upgrade'),
            ('Upgrade', 'websocket'),
            ('Sec-WebSocket-Key', self.key),
            ('Sec-WebSocket-Version', self.version)
        ]
        request = [("GET %s HTTP/1.1" % self.resource).encode('utf-8')]
        for header, value in headers:
            request.append(("%s: %s" % (header, value)).encode('utf-8'))
        request.append(b'\r\n')

        return b'\r\n'.join(request)
    
    def read_next_message(self):
        try:
            length = ord(self.rfile.read(2)[1]) & 127
            if length == 126:
                length = struct.unpack(">H", self.rfile.read(2))[0]
            elif length == 127:
                length = struct.unpack(">Q", self.rfile.read(8))[0]
            return self.rfile.read(length)
        except IndexError:
            self.close()
 
    def send(self, message):
        mask = [1,2,3,4]
        mask_bits = "".join([chr(x) for x in mask])
        
        self.wfile.write(chr(129))
        
        length = len(message)
        
        if length <= 125:
            self.wfile.write(chr(length ^ 128))
        elif length >= 126 and length <= 65535:
            self.wfile.write(chr(254))
            self.wfile.write(struct.pack(">H", length))
        else:
            self.wfile.write(chr(255))
            self.wfile.write(struct.pack(">Q", length))
        self.wfile.write(mask_bits)
        self.wfile.write(ws.apply_mask(message, mask))
        self.wfile.flush()

class TestWebSockets(test.ServerTestBase):
    handler = WebSocketsEchoHandler

    def test_basic_websockets_support(self):
        c = WebSocketsClient(("127.0.0.1", self.port))
        c.connect()
        msg  = "hello I'm the client"
        c.send(msg)
        response = c.read_next_message()
        print "Assert response: " + response  + "  == message: " + msg
        assert response == msg

    # test multiframe message support

    # test encrypted websockets support

    # test websockets passthrough

    # test websockets frame scripting

    # test websockets frame replay

    # test connection dying

    # test invalid upgrade

    # test 

