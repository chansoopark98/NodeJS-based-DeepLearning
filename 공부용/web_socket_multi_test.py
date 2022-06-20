import ssl
import asyncio
import websockets

import cv2
import numpy as np
import base64

from threading import Thread
from concurrent.futures import ProcessPoolExecutor

class TCPServer(object):
    def __init__(self, hostname, port, cert_dir, key_dir):
        self.hostname = hostname
        self.port = port
        self.cert_dir = cert_dir
        self.key_dir = key_dir
        self.configuration()



    def rcv_data(self, data):
        data = data[0]
        data = data.split(',')
        client_id = data[0]
        print('client id', client_id)
        base64_data = data[2]
        # print('base64_data', base64_data)
        

        if len(base64_data) % 4:
            # 4의 배수가 아니면 패딩
            base64_data += '=' * (4 - len(base64_data) % 4) 
            
        imgdata = base64.b64decode(base64_data)
        image = np.frombuffer(imgdata, np.uint8)
        image = cv2.imdecode(image, cv2.IMREAD_COLOR)


        cv2.imshow(str(client_id), image)
        # print(image.shape)
        cv2.waitKey(1)

        # encoding
        encode_image = base64.b64encode(image)
        return client_id, encode_image


    async def loop_logic(self, websocket, path):
        while True:

            try:
                # Wait data from client
                data = await asyncio.gather(websocket.recv())
                # data = await websocket.recv()
                client_id, rcv_data = self.rcv_data(data=data)

                await websocket.send(rcv_data);# 클라인언트로 echo를 붙여서 재 전송한다.

            except Exception as e:
                
                print('websocket client is disconnected!!  :', e)
                cv2.destroyWindow(str(client_id))


    def configuration(self):
        self.ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER) #PROTOCOL_TLS_SERVER
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
    # server.run_server()

    executor = ProcessPoolExecutor(max_workers=10)
    executor.map(server.run_server())
    # for _ in range(multiprocessing.cpu_count()):
    #     t = Thread(target=server.run_server)
    #     t.start()

    


    