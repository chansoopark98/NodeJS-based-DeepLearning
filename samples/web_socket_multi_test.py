import ssl
import asyncio
import websockets
import cv2
import numpy as np
import base64
import time
from dl_model.model_builder import SemanticModel
import tensorflow as tf

client_num = 1

class TCPServer(SemanticModel):
    def __init__(self, hostname, port, cert_dir, key_dir):
        super().__init__()
        self.hostname = hostname
        self.port = port
        self.cert_dir = cert_dir
        self.key_dir = key_dir

    async def rcv_data(self, data, gpu_name):
        data = data[0].split(',')
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

        start = time.process_time()
        output = self.model_predict(image=image, gpu_name=gpu_name)
        duration = (time.process_time() - start)
        # print("id: {0}, time: {1}".format(client_id, duration))

        cv2.imshow(str(client_id), image)
        cv2.waitKey(1)
        
        encode_image = cv2.imencode('.jpeg', image)
        encode_image = base64.b64encode(encode_image[1]).decode('utf-8')
        encode_image = 'data:image/jpeg;base64' + ',' + encode_image
        
        
        
        return client_id, encode_image

    async def loop_logic(self, websocket, path):
        global client_num
        if client_num % 2 == 1:
            gpu_name = '/device:GPU:0'
        else:
            gpu_name = '/device:GPU:1'

        print('client_num : {0},  gpu_num{1}'.format(client_num, gpu_name))
        client_num += 1
        # tf.debugging.set_log_device_placement(True)

        with tf.device(gpu_name):
            while True:
                try:
                    # Wait data from client
                    data = await asyncio.gather(websocket.recv())
                    client_id, rcv_data = await self.rcv_data(data=data, gpu_name=gpu_name)
                    
                    await websocket.send(rcv_data)

                except Exception as e:
                    print('Log : {0}'.format(e))
                    cv2.destroyWindow(str(client_id))
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
    use_local = True

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