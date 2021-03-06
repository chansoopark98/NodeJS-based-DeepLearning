from doctest import FAIL_FAST
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

docker run --runtime=nvidia -t -p 8500:8500 --rm -v "/home/park/park/Tensorflow-Keras-Realtime-Segmentation/checkpoints/export_path_trt:/models/test_model2" -e MODEL_NAME=test_model2 -e NVIDIA_VISIBLE_DEVICES="1" -e LD_LIBRARY_PATH=/usr/local/cuda-11.1/lib64:/usr/local/nvidia/lib:/usr/local/nvidia/lib64 -e TF_TENSORRT_VERSION=7.2.2 tensorflow/serving:2.6.2-gpu --port=8500 --num_load_threads=8 --tensorflow_session_parallelism=0 --tensorflow_intra_op_parallelism=4 --tensorflow_inter_op_parallelism=4

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


    async def get_data(self, data, session):
        base64_data = data[0]

        if len(base64_data) % 4:
            # 4??? ????????? ????????? ??????
            print('padding')
            base64_data += '=' * (4 - len(base64_data) % 4)

        imgdata = base64.b64decode(base64_data)
        image = np.frombuffer(imgdata, np.uint8)
        image = cv2.imdecode(image, cv2.IMREAD_COLOR)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        start = time.process_time()
        image = cv2.resize(image, (320, 240))
        image = image.astype(np.float32) / 255.
        
        # send_image = np.expand_dims(image, axis=0)
        
        output = await session.predict(image=image)

        output = output.outputs['output'].float_val
        output = np.array(output)
        output = np.reshape(output, (320, 240, 3))
        semantic_output = output[:, :, :2]
        semantic_output = np.argmax(semantic_output, axis=-1)
        duration = (time.process_time() - start)
        print("time: {0}".format(duration))
        semantic_output = semantic_output * 127

        # cv2.imshow(str(client_id), output.astype(np.uint8))
        cv2.imshow(str('1'), image)
        cv2.waitKey(1)
        
        encode_image = cv2.imencode('.jpeg', image)
        encode_image = base64.b64encode(encode_image[1]).decode('utf-8')
        encode_image = 'data:image/jpeg;base64' + ',' + encode_image

        return '1', encode_image
        

            
    async def loop_logic(self, websocket, path):
        global client_num
        
        address = '0.0.0.0:8500'

        async with RequestRestApi(address, 'test_model2') as session:
            print('client_num : {0}, address name {1}'.format(client_num, session.endpoint))
            client_num += 1
            while True:
                try:
                    # data = await websocket.recv()
                    data = await asyncio.gather(websocket.recv())
                    client_id, encode_image = await self.get_data(data=data, session=session)
                    # await websocket.send(encode_image)

                except Exception as e:
                    print('Log : {0}'.format(e))
                    cv2.destroyWindow(str(client_id))
                    await websocket.close()
                    client_num -= 1
                    break           

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