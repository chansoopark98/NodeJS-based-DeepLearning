import ssl
import asyncio
import websockets
import cv2
import numpy as np
import base64
import time
import tensorflow as tf
from aiogrpc import insecure_channel
from tensorflow_serving.apis import predict_pb2
from tensorflow_serving.apis import prediction_service_pb2_grpc
from concurrent.futures import ProcessPoolExecutor
from tensorflow.keras.applications.imagenet_utils import preprocess_input
import concurrent.futures
# docker run -t --gpus all --rm -p 8500:8500 -v "/home/park/park/NodeJS-based-DeepLearning/samples/dl_model/saved_model:/models/test_model" -e MODEL_NAME=test_model tensorflow/serving:2.6.2-gpu
# docker run -t --gpus all --rm -p 8500:8500 -v "/home/park/park/Tensorflow-Keras-Realtime-Segmentation/checkpoints/export_path:/models/test_model" -e MODEL_NAME=test_model tensorflow/serving:2.6.2-gpu
# /home/park/park/Tensorflow-Keras-Realtime-Segmentation/checkpoints/export_path/

# docker run -t --gpus all --rm -p 8500:8500 -v "/home/park/park/Tensorflow-Keras-Realtime-Segmentation/checkpoints/export_path:/models/test_model2" -e MODEL_NAME=test_model2 tensorflow/serving:2.6.2-gpu

"""
docker run --runtime=nvidia -t --gpus device=0 -p 8499:8499 --rm -v "/home/park/park/Tensorflow-Keras-Realtime-Segmentation/checkpoints/export_path:/models/test_model2" -e MODEL_NAME=test_model2 -e NVIDIA_VISIBLE_DEVICES="0" tensorflow/serving:2.6.2-gpu --port=8499 --rest_api_port=8501
docker run --runtime=nvidia -t -p 8499:8499 --rm -v "/home/park/park/Tensorflow-Keras-Realtime-Segmentation/checkpoints/export_path:/models/test_model2" -e MODEL_NAME=test_model2 -e NVIDIA_VISIBLE_DEVICES="0" tensorflow/serving:2.6.2-gpu --port=8499 --rest_api_port=8501
docker run --runtime=nvidia -t -p 8500:8500 --rm -v "/home/park/park/Tensorflow-Keras-Realtime-Segmentation/checkpoints/export_path:/models/test_model2" -e MODEL_NAME=test_model2 -e NVIDIA_VISIBLE_DEVICES="1" tensorflow/serving:2.6.2-gpu --port=8500 --rest_api_port=8501

# tensorRT
docker run -t --gpus device=1 -p 8499:8499 --rm -v "/home/park/park/Tensorflow-Keras-Realtime-Segmentation/checkpoints/export_path_trt:/models/test_model2" -e MODEL_NAME=test_model2 -e LD_LIBRARY_PATH=/usr/local/cuda-11.1/lib64:/usr/local/nvidia/lib:/usr/local/nvidia/lib64 tensorflow/serving:2.6.2-gpu --port=8499 --rest_api_port=8501

# tensorflow/serving:2.9.0-gpu
Tensorflow
docker run -t --gpus device=1 -p 8499:8499 --rm -v "/home/park/park/Tensorflow-Keras-Realtime-Segmentation/checkpoints/export_path:/models/test_model2" -e MODEL_NAME=test_model2 tensorflow/serving:2.9.0-gpu --port=8499 --rest_api_port=8501

TensorRT

docker run --runtime=nvidia -t -p 8497:8497 --rm -v "/home/park/park/Tensorflow-Keras-Realtime-Segmentation/checkpoints/export_path_trt:/models/test_model2" -e MODEL_NAME=test_model2 -e NVIDIA_VISIBLE_DEVICES="0" -e LD_LIBRARY_PATH=/usr/local/cuda-11.1/lib64:/usr/local/nvidia/lib:/usr/local/nvidia/lib64 -e TF_TENSORRT_VERSION=7.2.2 tensorflow/serving:2.6.2-gpu --port=8497 --num_load_threads=8 --tensorflow_session_parallelism=0 --tensorflow_intra_op_parallelism=4 --tensorflow_inter_op_parallelism=4 --per_process_gpu_memory_fraction=0.3

docker run --runtime=nvidia -t -p 8498:8498 --rm -v "/home/park/park/Tensorflow-Keras-Realtime-Segmentation/checkpoints/export_path_trt:/models/test_model2" -e MODEL_NAME=test_model2 -e NVIDIA_VISIBLE_DEVICES="0" -e LD_LIBRARY_PATH=/usr/local/cuda-11.1/lib64:/usr/local/nvidia/lib:/usr/local/nvidia/lib64 -e TF_TENSORRT_VERSION=7.2.2 tensorflow/serving:2.6.2-gpu --port=8498 --num_load_threads=8 --tensorflow_session_parallelism=0 --tensorflow_intra_op_parallelism=4 --tensorflow_inter_op_parallelism=4 --per_process_gpu_memory_fraction=0.3

docker run --runtime=nvidia -t -p 8499:8499 --rm -v "/home/park/park/Tensorflow-Keras-Realtime-Segmentation/checkpoints/export_path_trt:/models/test_model2" -e MODEL_NAME=test_model2 -e NVIDIA_VISIBLE_DEVICES="1" -e LD_LIBRARY_PATH=/usr/local/cuda-11.1/lib64:/usr/local/nvidia/lib:/usr/local/nvidia/lib64 -e TF_TENSORRT_VERSION=7.2.2 tensorflow/serving:2.6.2-gpu --port=8499 --num_load_threads=8 --tensorflow_session_parallelism=0 --tensorflow_intra_op_parallelism=4 --tensorflow_inter_op_parallelism=4 --per_process_gpu_memory_fraction=0.3

docker run --runtime=nvidia -t -p 8500:8500 --rm -v "/home/park/park/Tensorflow-Keras-Realtime-Segmentation/checkpoints/export_path_trt:/models/test_model2" -e MODEL_NAME=test_model2 -e NVIDIA_VISIBLE_DEVICES="0" -e LD_LIBRARY_PATH=/usr/local/cuda-11.1/lib64:/usr/local/nvidia/lib:/usr/local/nvidia/lib64 -e TF_TENSORRT_VERSION=7.2.2 tensorflow/serving:2.6.2-gpu --port=8500

"""


client_num = 1
avg_time = []


class RequestRestApi(object):
    def __init__(self, host_name, model_name):
        self.endpoint = host_name
        self.model_name = model_name

    async def __aenter__(self):
        self._channel = insecure_channel(self.endpoint)
        self._stub = prediction_service_pb2_grpc.PredictionServiceStub(self._channel)
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self._channel.close()

    async def predict(self, image):
        self.request = predict_pb2.PredictRequest()
        self.request.model_spec.name = self.model_name
        self.request.inputs['input_1'].CopyFrom(
        tf.make_tensor_proto(image, shape=[1, 320, 240, 3]))
        return await self._stub.Predict(self.request, 5.0)


class TCPServer():
    def __init__(self, hostname, port, cert_dir, key_dir):
        super().__init__()
        self.hostname = hostname
        self.port = port
        self.cert_dir = cert_dir
        self.key_dir = key_dir
        self.loop = asyncio.new_event_loop()
        self.tcp_address = 'http://localhost:8501/v1/models/test_model:predict'       


    def calc_pca(self, img, mask):
        img_h = mask.shape[0]
        img_w = mask.shape[1]

        # Get display area
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if len(contours) == 0:
            return []

        display_contours = sorted(contours, key=cv2.contourArea, reverse=True)
                
        x,y,w,h = cv2.boundingRect(display_contours[0])
        area = cv2.contourArea(display_contours[0])

        center_x = x + (w//2)
        center_y = y + (h//2)

        roll =0
        pitch = 0
        yaw = 0
        area = 0

        return [center_x, center_y, roll, pitch, yaw, area, w, h]

    async def get_data(self, data, session, websocket):
        base64_data = data[0]

        if len(base64_data) % 4:
            # 4의 배수가 아니면 패딩
            print('padding')
            base64_data += '=' * (4 - len(base64_data) % 4)

        imgdata = base64.b64decode(base64_data)
        image = np.frombuffer(imgdata, np.uint8)
        image = cv2.imdecode(image, cv2.IMREAD_COLOR)

        start = time.process_time()
        image = cv2.resize(image, (240, 320))

        # image = (image / 127.5) -1.
        image = image.astype(np.float32)
        image = preprocess_input(image, mode='tf')  

        output = await session.predict(image=image)

        output = output.outputs['output'].float_val
        output = np.array(output)
        output = np.reshape(output, (320, 240, 3))
        semantic_output = output[:, :, :2]
        semantic_output = np.argmax(semantic_output, axis=-1)
        semantic_output = np.expand_dims(semantic_output, axis=-1)
        semantic_output = semantic_output.astype(np.uint8) * 127
        cv2.imshow('test', semantic_output)
        cv2.waitKey(1)
        
        
        
        calc_pca = self.calc_pca(img=image, mask=semantic_output)

        if len(calc_pca) != 0:
            center_x, center_y, roll, pitch, yaw, area, w, h = calc_pca

            # sift x coord
            align_center_x = 240 // 2
            if center_x >= align_center_x:
                center_x -= int(w * 0.8)

                if center_x <= 0:
                    center_x = 0    

            else:
                center_x += int(w * 0.8)
                
                if center_x >= 240:
                    center_x = 240
            

            # re-scale x,y coords
            Rx = 720/240
            Ry = 1280/320
            rescale_center_x = round(Rx * center_x)
            rescale_center_y = round(Ry * center_y)


            encode_image = str(rescale_center_x) + ',' + str(rescale_center_y) + \
                ',' + str(roll) + ',' + str(pitch) + ',' + str(yaw) + \
                ',' + str(int(area)) + ',' + str(w) + ',' + str(h)
            
            await websocket.send(encode_image)
            # return encode_image
        

            
    async def loop_logic(self, websocket, path):
        global client_num
        
        address = '0.0.0.0:8500'

        async with RequestRestApi(address, 'test_model2') as session:
            print('client_num : {0}, address name {1}'.format(client_num, session.endpoint))
            client_num += 1
            while True:
                # try:
                    
                data = await asyncio.gather(websocket.recv())
                await self.get_data(data=data, session=session, websocket=websocket)
                


                # except Exception as e:
                # print('Log :1 {0}'.format(e))
                # await websocket.close()
                # client_num -= 1
                    # break           

    async def run_server(self):
        self.ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        self.ssl_context.load_cert_chain(self.cert_dir, self.key_dir)
        if use_local:
            self.ssl_context = None
        self.start_server = websockets.serve(self.loop_logic,
                                             port=self.port, ssl=self.ssl_context,
                                             max_size=150000,
                                             max_queue=4,
                                             read_limit=2**16,
                                             write_limit=2**15)
                      
        # asyncio.get_event_loop().run_until_complete(self.start_server)
        # asyncio.get_event_loop().run_forever()

        async with self.start_server:
            print(self.start_server)
            await asyncio.Future()
        


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
    # server.run_server()
    with concurrent.futures.ProcessPoolExecutor() as pool:
        server.loop.run_in_executor(pool, asyncio.run(server.run_server()))