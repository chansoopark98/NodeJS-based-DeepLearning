from audioop import mul
import multiprocessing
import socket
import base64
import cv2
from PIL import Image
import io
import numpy as np
from imageio import imread
import logging

connects = [1, 2]

def handle(connection, address):
    connect_name = connects.pop(0)
    print("Connection:", connection, "  address: ", address)
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger("process-%r" % (address,))

    try:
        logger.debug("Connected %r at %r", connection, address)
        while True:
            
            data = connection.recv(100000)
            
            data = data.split(b',')

            client_id = data[0]
            client_id = client_id.decode('utf-8')
            base64_data = data[2]
            print('client_id', client_id)
            
            print('len', len(base64_data))
            # data = data.decode('base64')
            if len(base64_data) % 4:
                # 4의 배수가 아니면 패딩
                base64_data += b'=' * (4 - len(base64_data) % 4) 
                
            imgdata = base64.b64decode(base64_data)
            image = np.fromstring(imgdata, np.uint8)
            image = cv2.imdecode(image, cv2.IMREAD_COLOR)

            # image = Image.open(io.BytesIO(imgdata))
            # image = Image.open(imgdata)
            # image = np.array(image)
            cv2.imshow(str(client_id), image)
            cv2.waitKey(1)

            # encoding
            encode_image = base64.b64encode(image)
            connection.send(encode_image)

    except:
        logger.exception("핸들링 요청에서 에러 발생")
    finally:
        logger.debug("소켓 연결 종료")
        connection.close()


class TCPServer(object):
    def __init__(self, hostname, port):
        self.hostname= hostname
        self.port = port

    
    def start(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.hostname, self.port))
        self.server_socket.listen()

        while True:
            conn, address = self.server_socket.accept()
            process = multiprocessing.Process(target=handle, args=(conn, address))
            process.daemon = True
            process.start()


if __name__ == "__main__":
    server = TCPServer(hostname='127.0.0.1', port=7777)
    server.start()