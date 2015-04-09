# import server from netlib
from netlib import tcp
from netlib.websockets import WebSocketsEchoHandler, WebSocketsClient
from netlib import test

# import client from 3rd party TODO replace
from websocket import create_connection



class TestWebSockets(test.ServerTestBase):
    handler = WebSocketsEchoHandler

    # test that a successful websockets connection can be made through
    # mitmproxy and that messages can be passed in each direction.
    def test_basic_websockets_support(self):

        c = WebSocketsClient(("127.0.0.1", self.port))
        c.connect()

        msg  = "hello I'm the client"
        
        print "test tell client to send: " + msg

        c.send(msg)
        # import time
        # time.sleep(5)

        print "test waiting for server to respond to message"
        response = c.read_next_message()

        if response:
          print "test got this response from server: " + response
        else:
          print "test got none from server"
        
        c.close()

# class EchoHandler(tcp.BaseHandler):
#     sni = None
#     def handle_sni(self, connection):
#         self.sni = connection.get_servername()

#     def handle(self):
#         v = self.rfile.readline()
#         self.wfile.write(v)
#         self.wfile.flush()

#         v = self.rfile.read(1)
#         self.wfile.write(v)
#         self.wfile.flush()

# class TestServer(test.ServerTestBase):
#     handler = EchoHandler
#     def test_echo(self):
#         testval = "echo!\n"
#         testval2 = "echo!2\n"
#         print self.port
#         c = tcp.TCPClient(("127.0.0.1", self.port))
#         c.connect()
#         c.wfile.write(testval)
#         c.wfile.flush()
#         assert c.rfile.readline() == testval

#         c.wfile.write(testval2)
#         c.wfile.flush()
#         got = c.rfile.readline()
#         print "got: " + got
#         print "testval2: " + testval2
#         assert got == testval2




        # print "\n\n\n"
        


    # test multiframe message support

    # test encrypted websockets support

    # test websockets passthrough

    # test websockets frame scripting

    # test websockets frame replay

    # test connection dying

    # test invalid upgrade

    # test 


    # def test_invalid_connect(self):
    #     t = tcp.TCPClient(("127.0.0.1", self.proxy.port))
    #     t.connect()
    #     t.wfile.write("GET http://www.google.com HTTP/1.1\r\n")
    #     t.wfile.flush()
    #     print t.rfile.readline()

    # def test_app_err(self):
    #     p = self.pathoc()
    #     ret = p.request("get:'http://google.com'")
    #     print ret
    #     assert ret.status_code == 500
    #     assert "ValueError" in ret.content

    # def test_double_connect(self):
    #     p = self.pathoc()
    #     r = p.request("get :'%s:%s'" % ("127.0.0.1", self.server2.port))
    #     assert r.status_code == 400
    #     assert "Must not CONNECT on already encrypted connection" in r.content
