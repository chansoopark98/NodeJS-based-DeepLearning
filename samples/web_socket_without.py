import ssl
import asyncio
import websockets
import cv2
import numpy as np
import base64
import mediapipe as mp

mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(max_num_faces=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils
drawing_spec = mp_drawing.DrawingSpec(thickness=1, circle_radius=1)


class TCPServer():
    def __init__(self, hostname, port, cert_dir, key_dir):
        super().__init__()
        self.hostname = hostname
        self.port = port
        self.cert_dir = cert_dir
        self.key_dir = key_dir

        self.width = 1920
        self.height = 1080
        self.focal_length = 1 * self.width
        self.cam_matrix = np.array([[self.focal_length, 0, self.height/2],
                                    [0, self.focal_length, self.width/2],
                                    [0, 0, 1]])
        self.cam_matrix = np.array(self.cam_matrix)
        self.dist_matrix = np.zeros((4, 1), dtype=np.float64)

    def rcv_data(self, data, websocket):

        # print(data)

        base64_data = data[0]
        
        # if len(base64_data) % 4:
        #     # 4의 배수가 아니면 패딩
        #     print('padding')
        #     base64_data += '=' * (4 - len(base64_data) % 4)
        
        imgdata = base64.b64decode(base64_data)
        image = np.frombuffer(imgdata, np.uint8)
        image = cv2.imdecode(image, cv2.IMREAD_COLOR)



        
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
        results = face_mesh.process(image)
        image.flags.writeable = True

        face_2d = []
        face_3d = []
        output = []
        idx = 0
        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                idx += 1
                for idx, lm in enumerate(face_landmarks.landmark):
                    # if idx == 33 or idx == 263 or idx == 1 or idx == 61 or idx == 291 or idx == 199:
                        if idx == 1:
                            center_x = int(lm.x * self.width)
                            center_y = int(lm.y * self.height)
                        x = int(lm.x * self.width)
                        y = int(lm.y * self.height)


                        face_2d.append([x,y])
                        face_3d.append([x, y, lm.z])
    
        
        # for i in range(0, 18, 3):
        #     x = float(data[i])
        #     y = float(data[i+1])
        #     z = float(data[i+2])

        



                face_2d = np.array(face_2d, dtype=np.float64)
                face_3d = np.array(face_3d, dtype=np.float64)

                success, rot_vec, trans_vec = cv2.solvePnP(face_3d, face_2d, self.cam_matrix, self.dist_matrix)

                rmat, jac = cv2.Rodrigues(rot_vec)

                angle, mtxR, mtxQ, Qx, Qy, Qz = cv2.RQDecomp3x3(rmat)


                # print(angle)
            # center_x = str(center_x) + ','
            # center_y = str(center_y) + ','
            center_x = str(960) + ','
            center_y = str(400) + ','
            x_rot = str(angle[0] ) + ','
            y_rot = str(round(angle[1], 3)) + ','
            z_rot = str(angle[2]) + ','
            
            print(round(angle[1], 3))
            output = center_x + center_y +x_rot + y_rot + z_rot

            
        
        return output
        
        
        
        

    async def loop_logic(self, websocket, path):


        while True:
                
            # Wait data from client
            data = await asyncio.gather(websocket.recv())
            rcv_data = self.rcv_data(data=data, websocket=websocket)
            if rcv_data != 0:
                await websocket.send(rcv_data)





    
    def run_server(self):
        self.ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        self.ssl_context.load_cert_chain(self.cert_dir, self.key_dir)
        if use_local:
            self.ssl_context = None
        self.start_server = websockets.serve(self.loop_logic,
                                             port=self.port, ssl=self.ssl_context,
                                             max_size=200000,
                                             max_queue=1,
                                             read_limit=2**20,
                                             write_limit=2**8)
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