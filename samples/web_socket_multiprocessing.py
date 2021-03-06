import ssl
import asyncio
import websockets
import cv2
import numpy as np
import base64
import time
from dl_model.model_builder import SemanticModel
import tensorflow as tf
from websockets.extensions import permessage_deflate
import concurrent.futures

client_num = 1


class TCPServer(SemanticModel):
    def __init__(self, hostname, port, cert_dir, key_dir):
        super().__init__()
        self.hostname = hostname
        self.port = port
        self.cert_dir = cert_dir
        self.key_dir = key_dir
        self.loop = asyncio.new_event_loop()
        

    async def rcv_data(self, data, gpu_name, usr_id, websocket):
        base64_data = data[0]

        imgdata = base64.b64decode(base64_data)
        image = np.frombuffer(imgdata, np.uint8)
        image = cv2.imdecode(image, cv2.IMREAD_COLOR)
        image = cv2.resize(image, (240, 320))
        # image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        start = time.process_time()
        output = self.model_predict(image=image, gpu_name=gpu_name)
        
        
        calc_pca = self.calc_pca(img=image, mask=output)
        if len(calc_pca) != 0:
            center_x, center_y, roll, pitch, yaw, area, w, h = calc_pca
    
            duration = (time.process_time() - start)
            # print("time: {0}".format(duration))
            

            cv2.circle(output, (int(center_x), int(center_y)), int(3), (0, 0, 255), 3, cv2.LINE_AA)
            output = cv2.cvtColor(output, cv2.COLOR_GRAY2BGR)

            
            # image = cv2.hconcat([image, output])

            cv2.imshow(usr_id, output)
            cv2.waitKey(1)

            
            # sift x coord
            align_center_x = 240 // 2
            if center_x >= align_center_x:
                center_x -= int(w * 0.85)

                if center_x <= 0:
                    center_x = 0    

            else:
                center_x += int(w * 0.85)
                
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
    # return usr_id, encode_image

    async def loop_logic(self, websocket):
        global client_num
        if client_num % 2 == 1:
            gpu_name = '/device:GPU:0'
        else:
            gpu_name = '/device:GPU:1'
        usr_id = str(client_num)
        print('client_num : {0},  gpu_num{1}'.format(client_num, gpu_name))
        client_num += 1
    
        while True:
            try:
                # Wait data from client
                data = await asyncio.gather(websocket.recv())
                await self.rcv_data(data=data, gpu_name=gpu_name, usr_id=usr_id, websocket=websocket)
                
                # await websocket.send(rcv_data)
                

            except Exception as e:
                client_num -= 1
                websocket.close()
                print('Log error : {0}'.format(e))
                cv2.destroyWindow(usr_id)
                break
                

    
    async def run_server(self):
        print('run_server')
        self.ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        self.ssl_context.load_cert_chain(self.cert_dir, self.key_dir)
        if use_local:
            self.ssl_context = None
        self.start_server = websockets.serve(self.loop_logic,
                                             port=self.port, ssl=self.ssl_context,
                                             max_size=100000,
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
            
