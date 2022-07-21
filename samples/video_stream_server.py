from flask import Flask
from flask import request
from flask import Response
from flask import stream_with_context
import flask_cors

import ssl

from video_stream_streamer import Streamer

app = Flask( __name__ )
flask_cors.CORS(app)
streamer = Streamer()

@app.route('/stream')
def stream():
    
    src = request.args.get( 'src', default = 0, type = int )
    
    try :
        # mimetype='video/mp4',
                        # content_type='video/mp4', direct_passthrough=True)
        return Response(
                                stream_with_context( stream_gen( src ) ),
                                mimetype='multipart/x-mixed-replace; boundary=frame')
        
        # return Response(
        #                         stream_with_context( stream_gen( src ) ),
        #                         mimetype='multipart/x-mixed-replace; boundary=frame' )
        
    except Exception as e :
        
        print('[wandlab] ', 'stream error : ',str(e))

def stream_gen( src ):   
  
    try :
        
        streamer.run( src )
        
        while True :
            
            frame = streamer.bytescode()
            
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
                    
    except GeneratorExit :
        #print( '[wandlab]', 'disconnected stream' )
        streamer.stop()


if __name__ == '__main__':
    cert_dir = '../cert.pem'
    key_dir = '../privkey.pem'

    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ssl_context.load_cert_chain(cert_dir, key_dir)
    app.run(host='0.0.0.0', port=4447, ssl_context=ssl_context)    
    # http://:4447/stream?src=0