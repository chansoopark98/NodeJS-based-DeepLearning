import asyncio
import ssl
import cv2
import time
import numpy as np
import base64
import wsaccel

wsaccel.patch_autobahn()
from autobahn.asyncio.websocket import WebSocketServerProtocol, \
    WebSocketServerFactory


class MyServerProtocol(WebSocketServerProtocol):

    def onConnect(self, request):
        print("Client connecting: {0}".format(request.peer))

    def onOpen(self):
        print("WebSocket connection open.")

    def onMessage(self, payload, isBinary):
    
        start = time.process_time()
        # get message payload
        data = payload.decode('utf8')
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

        
        # output = self.model_predict(image=image, gpu_name=gpu_name)
        

        cv2.imshow(str(client_id), image)
        cv2.waitKey(1)
        
        encode_image = cv2.imencode('.jpeg', image)
        encode_image = base64.b64encode(encode_image[1]).decode('utf-8')
        encode_image = 'data:image/jpeg;base64' + ',' + encode_image

        # echo back message verbatim
        self.sendMessage(payload, isBinary)
        duration = (time.process_time() - start)
        print("id: {0}, time: {1}".format(client_id, duration))

    def onClose(self, wasClean, code, reason):
        print("WebSocket connection closed: {0}".format(reason))


if __name__ == '__main__':
    from multiprocessing import Process
    import concurrent
    local_mode = True

    cert_dir = '../cert.pem'
    key_dir = '../privkey.pem'
    
    
    if local_mode:
        address = 'ws://127.0.0.1:7777'
        ssl_context = None
    else:
        address = 'wss://park-tdl.tspxr.ml:7777'
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ssl_context.load_cert_chain(cert_dir, key_dir)

    factory = WebSocketServerFactory(address)
    factory.setProtocolOptions(tcpNoDelay=True)
    factory.protocol = MyServerProtocol

    def worker(id):
        id += 1
        port = 7777
        if id % 2 == 0:
            port = 7778
        loop = asyncio.get_event_loop()
    
        coro = loop.create_server(factory, '0.0.0.0', port, ssl=ssl_context,)
    
        server = loop.run_until_complete(coro)
        
        
        loop.run_forever()

    # p = Process(target=worker)
    # p.start()
    # p.join()

    plist = list()
    print('for range')
    for i in range(2):
        p = Process(
            target=worker(i)
            ,)
        plist.append(p)
    print('for start')
    for proc in plist:
        proc.start()
    print('for join')
    for proc in plist:
        proc.join()
        

    # try:
    #     loop.run_forever()
    # except KeyboardInterrupt:
    #     pass
    # finally:
    #     server.close()
    #     loop.close()