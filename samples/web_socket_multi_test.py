import ssl
import asyncio
import websockets
import cv2
import numpy as np
import base64
from threading import Thread
from dl_model.model_builder import SemanticModel


class TCPServer(SemanticModel):
    def __init__(self, hostname, port, cert_dir, key_dir):
        super().__init__()
        self.hostname = hostname
        self.port = port
        self.cert_dir = cert_dir
        self.key_dir = key_dir

    def rcv_data(self, data):
        data = data[0].split(',')
        client_id = data[0]
        base64_data = data[2]

        if len(base64_data) % 4:
            # 4의 배수가 아니면 패딩
            base64_data += '=' * (4 - len(base64_data) % 4)

        imgdata = base64.b64decode(base64_data)
        image = np.frombuffer(imgdata, np.uint8)
        image = cv2.imdecode(image, cv2.IMREAD_COLOR)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        predict = self.model_predict(image=image)
        predict = predict[0]
        cv2.imshow(str(client_id), predict.astype(np.uint8)*255)
        cv2.waitKey(1)

        encode_image = base64.b64encode(image)
        return client_id, encode_image

    async def loop_logic(self, websocket, path):
        while True:

            try:
                # Wait data from client
                data = await asyncio.gather(websocket.recv())
                client_id, rcv_data = self.rcv_data(data=data)

                await websocket.send(rcv_data)

            except Exception as e:
                print('websocket client is disconnected!!  :', e)
                cv2.destroyWindow(str(client_id))

    
    def run_server(self):
        self.ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        self.ssl_context.load_cert_chain(self.cert_dir, self.key_dir)
        self.start_server = websockets.serve(self.loop_logic,
                                             port=self.port, ssl=self.ssl_context,
                                             max_size=100000,
                                             max_queue=4,
                                             read_limit=2**16)
        asyncio.get_event_loop().run_until_complete(self.start_server)
        asyncio.get_event_loop().run_forever()
        

if __name__ == "__main__":
    server = TCPServer(
        hostname = '0.0.0.0',
        port = 7777,
        cert_dir = '../cert.pem',
        key_dir = '../privkey.pem'
    )
    loop_server = Thread(target=server.run_server(), daemon=True)
    loop_server.start()

    


    