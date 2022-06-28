import ssl
import asyncio
import websockets
import cv2
import numpy as np
import base64
from threading import Thread
from dl_model.model_builder import SemanticModel
import requests
import json


class TCPServer():
    def __init__(self, hostname, port, cert_dir, key_dir):
        super().__init__()
        self.hostname = hostname
        self.port = port
        self.cert_dir = cert_dir
        self.key_dir = key_dir
        self.tcp_address = 'http://localhost:8501/v1/models/test_model:predict'


    async def get_data(self, data, websocket):
        data = data[0].split(',')
        
        self.client_id = data[0]
        data_type = data[1]
        base64_data = data[2]

        if len(base64_data) % 4:
            # 4의 배수가 아니면 패딩
            base64_data += '=' * (4 - len(base64_data) % 4)

        imgdata = base64.b64decode(base64_data)
        image = np.frombuffer(imgdata, np.uint8)
        image = cv2.imdecode(image, cv2.IMREAD_COLOR)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = cv2.resize(image, (180, 320))

        # Send to Tensorflow docker's
        send_image = np.expand_dims(image, axis=0)

        send_image = json.dumps({'instances':send_image[0:3].tolist()})
        
        result = requests.post(self.tcp_address, data=send_image)

        predictions = json.loads(str(result.content, 'utf-8'))['predictions']

        prediction = np.array(predictions[0])
        prediction = np.reshape(prediction, (320, 180, 2))
        prediction = np.argmax(prediction, axis=-1)
        prediction = prediction * 127
        
        cv2.imshow(str(self.client_id), image)
        cv2.waitKey(1)
        


        encode_image = cv2.imencode('.jpeg', image)
        encode_image = base64.b64encode(encode_image[1]).decode('utf-8')
        encode_image = 'data:image/jpeg;base64' + ',' + encode_image

        await websocket.send(encode_image)
        
        
        

    async def loop_logic(self, websocket, path):

        while True:
            try:
                # Wait data from client
                data = await asyncio.gather(websocket.recv())
                
                # data = await websocket.recv()
                
                
                # client_id, rcv_data = await self.get_data(data=data)
                await self.get_data(data=data, websocket=websocket)
                
                
            
                # client_id, rcv_data = self.rcv_data(data=data)
                

            except Exception as e:
                print('Log : {0}'.format(e))
                cv2.destroyWindow(str(self.client_id))
                break
                # websocket.close()

    
    def run_server(self):
        self.ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        self.ssl_context.load_cert_chain(self.cert_dir, self.key_dir)
        if use_local:
            self.ssl_context = None
        self.start_server = websockets.serve(self.loop_logic,
                                             port=self.port, ssl=self.ssl_context,
                                             max_size=100000,
                                             max_queue=128,
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
    # server.save_model()
    server.run_server()