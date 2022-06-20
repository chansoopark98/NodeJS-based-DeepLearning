import ssl
import asyncio
import websockets


class TCPServer(object):
    def __init__(self, hostname, port, cert_dir, key_dir):
        self.hostname = hostname
        self.port = port
        self.cert_dir = cert_dir
        self.key_dir = key_dir
        self.configuration()


    async def loop_logic(self, websocket, path):
        while True:
            # Wait data from client
            data = await websocket.recv()
            print("receive : " + data)

            # TODO (logic)
            # ..

            # Return to client
            await websocket.send("ws_srv send data = " + data);# 클라인언트로 echo를 붙여서 재 전송한다.


    def configuration(self):
        self.ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        self.ssl_context.load_cert_chain(self.cert_dir, self.key_dir)
        self.start_server = websockets.serve(self.loop_logic, port=self.port, ssl=self.ssl_context)

    
    def run_server(self):
        asyncio.get_event_loop().run_until_complete(self.start_server)
        asyncio.get_event_loop().run_forever()


if __name__ == "__main__":
    server = TCPServer(
        hostname = '0.0.0.0',
        port = 7777,
        cert_dir = '../cert.pem',
        key_dir = '../privkey.pem'
    )
    server.run_server()