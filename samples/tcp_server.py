import ssl
import asyncio
import websockets
import cv2
import numpy as np
import base64


class TCPServer():
    def __init__(self, hostname, port, cert_dir, key_dir):
        super().__init__()
        self.hostname = hostname
        self.port = port
        self.cert_dir = cert_dir
        self.key_dir = key_dir


    async def get_data(self, image, session):
        """
        Args:
        data -> cliend_id + data_type + base64_data
        client_id : 웹 클라이언트에서 난수로 생성한 str type data
        data_type : 'data:image/jpeg;base64' (jpeg)
        base64_data : base64로 인코딩된 str type data
        """
        data = data.split(',')
        client_id = data[0]
        data_type = data[1]
        base64_data = data[2]

        if len(base64_data) % 4:
            # 4의 배수가 아니면 패딩
            base64_data += '=' * (4 - len(base64_data) % 4)

        imgdata = base64.b64decode(base64_data)
        image = np.frombuffer(imgdata, np.uint8)
        image = cv2.imdecode(image, cv2.IMREAD_COLOR)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        encode_image = cv2.imencode('.jpeg', image)
        encode_image = base64.b64encode(encode_image[1]).decode('utf-8')
        encode_image = 'data:image/jpeg;base64' + ',' + encode_image

        return client_id, encode_image
        

            
    async def loop_logic(self, websocket, path):
        while True:
            try:
                # 웹 클라이언트에서 웹소켓으로 데이터 전송
                data = await websocket.recv()

                # TODO
                # 이 부분 추가해서 사용하시면 됩니다
                _, rcv_data = await self.get_data(image=data) 

                # 웹 클라이언트로 데이터 전송
                await websocket.send(rcv_data)

            except Exception as e:
                print('Log : {0}'.format(e))
                websocket.close()
                break
                    

    def run_server(self):
        self.ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        self.ssl_context.load_cert_chain(self.cert_dir, self.key_dir)
        if use_local:
            self.ssl_context = None
        self.start_server = websockets.serve(self.loop_logic,
                                             port=self.port, ssl=self.ssl_context,
                                             max_size=150000,
                                             max_queue=1,
                                             read_limit=2**20,
                                             write_limit=2**20)
                                               
        asyncio.get_event_loop().run_until_complete(self.start_server)
        asyncio.get_event_loop().run_forever()
        

if __name__ == "__main__":
    use_local = False

    if use_local:
        hostname = '127.0.0.1'
    else:
        hostname = '0.0.0.0'

    server = TCPServer(
        hostname = hostname,
        port = 7777,
        cert_dir = '../cert.pem',
        key_dir = '../privkey.pem'
    )
    server.run_server()