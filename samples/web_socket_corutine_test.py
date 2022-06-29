from pydoc import cli
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
import time
import aiotf
import tensorflow as tf
import grpc

from tensorflow_serving.apis import predict_pb2
from tensorflow_serving.apis import prediction_service_pb2_grpc


async def make_prediction(model_name: str, data):
        value = 0
        async with aiotf.AsyncTensorflowServing('localhost:8501') as client:
            predictions = client.predict(model_name, data)
            # value =tf.make_ndarray(predictions.outputs['output'])
            value = predictions
        return value

        
class TCPServer():
    def __init__(self, hostname, port, cert_dir, key_dir):
        super().__init__()
        self.hostname = hostname
        self.port = port
        self.cert_dir = cert_dir
        self.key_dir = key_dir
        self.tcp_address = 'http://localhost:8501/v1/models/test_model:predict'       

        # self.channel = grpc.insecure_channel('localhost:8500', options=(('grpc.enable_http_proxy', 0),))
        self.channel = grpc.insecure_channel('localhost:8500')
        self.stub = prediction_service_pb2_grpc.PredictionServiceStub(self.channel)


    async def get_data(self, data):
        # data = data[0].split(',')
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
        image = cv2.resize(image, (180, 320))
        image = image.astype(np.float32) / 255.
        
        send_image = np.expand_dims(image, axis=0)
        
        # send_image = json.dumps({'instances':send_image[0:3].tolist()})
        # output = self.client.predict('test_model', send_image)

        
        # result = requests.post(self.tcp_address, data=send_image)

        # predictions = json.loads(str(result.content, 'utf-8'))['predictions']

        # prediction = np.array(predictions[0])
        # prediction = np.reshape(prediction, (320, 180, 2))
        # prediction = np.argmax(prediction, axis=-1)
        # prediction = prediction * 127

        request = predict_pb2.PredictRequest()
        request.model_spec.name = 'test_model'
        # request.model_spec.signature_name = 'serving_default'
        request.inputs['input_1'].CopyFrom(
        tf.make_tensor_proto(send_image, shape=[1, 320, 180, 3]))
        result = self.stub.Predict(request, 10.0)  # 10 secs timeout
        output = result.outputs['output'].float_val
        output = np.array(output)
        output = np.reshape(output, (320, 180, 2))
        output = np.argmax(output, axis=-1)
        output = output * 127

        cv2.imshow(str(client_id), output.astype(np.uint8))
        cv2.waitKey(1)
        
        
        # encode_image = cv2.imencode('.jpeg', output[0].numpy())
        encode_image = cv2.imencode('.jpeg', image)
        encode_image = base64.b64encode(encode_image[1]).decode('utf-8')
        encode_image = 'data:image/jpeg;base64' + ',' + encode_image

        
        # websocket.send(encode_image)
        return client_id, encode_image
        

            
        

    async def loop_logic(self, websocket, path):
        while True:
            try:
                start = time.process_time()
                # Wait data from client
                # data = await asyncio.gather(websocket.recv())
                data = await websocket.recv()
                
                # client_id, rcv_data = await self.get_data(data=data)
                client_id, encode_image = await self.get_data(data=data)
                await websocket.send(encode_image)
                
                
                duration = (time.process_time() - start)
                print("id: {0}, time: {1}".format(client_id, duration))
                # client_id, rcv_data = self.rcv_data(data=data)
                

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
    # server.save_model()
    server.run_server()