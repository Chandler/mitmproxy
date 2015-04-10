from netlib import tcp
from netlib import test
from netlib.websockets import implementations as ws
import netlib
import tservers

class TestWebSocketsSupport(test.ServerTestBase, tservers.HTTPProxTest):
    handler = ws.WebSocketsEchoHandler


    def test_websockets_echo(self):
        msg    = "hello I'm the client"
        client = ws.WebSocketsClient(("127.0.0.1", self.port), ("127.0.0.1", self.proxy.port))
        client.connect()
        client.send_message(msg)
        response = client.read_next_message()
        assert response == msg
