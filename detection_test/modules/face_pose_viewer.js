// tf.ENV.set("WEBGL_CPU_FORWARD", true)
// tf.setBackend('webgl');
// // tf.setBackend('wasm');
// console.log(tf.getBackend()); // tf backend 확인

import * as camera_util from "./camera.js";
import { render_ar_video, switch_visible, get_world_coords, get_world_rotate, visibleHandler} from "./face_pose_ar.js";

var webSocket = new WebSocket("wss://park-tdl.tspxr.ml:7777");

// 이미지를 저장하기 위한 canvas 생성


const canvas = document.getElementById("render_area");
canvas.width=1920;
canvas.height=1080;

var target_loop = 0;
var idx;
var face_idx;
var center_x;
var center_y;
var x_rot;
var y_rot;
var z_rot;
var depth;

var visibleFlag= false;


let context = canvas.getContext('2d');
                
var videoElement = document.getElementById('video');

videoElement.addEventListener('canplaythrough', render_video);
console.log(videoElement.videoWidth, videoElement.videoHeight);


// videoElement.width = 720;
// videoElement.height = 1280;


// 페이지를 로드하면 실행 (구성요소들 초기화)
function onLoad() {
    console.log('on load')
    // canvas.width = width;
    // canvas.height = height;
    camera_util.getCamera(videoElement);
}


webSocket.interval = setInterval(() => { // ?초마다 클라이언트로 메시지 전송
    if (webSocket.readyState === webSocket.OPEN) {
        
        var sendData = canvas.toDataURL('image/jpeg', 0.3)
        webSocket.send(sendData.split(",")[1]);
        
    }
}, 50);

webSocket.onmessage = function(message){
    visibleFlag = true;
    var recv_data = message.data.split(',');
    

    target_loop = recv_data.length/7
    
    for (let i=1; i<=target_loop; i++){

        idx = i * 7;
        face_idx = parseInt(recv_data[idx-7]);
        
        center_x = parseFloat(recv_data[idx-6]);
        center_y = parseFloat(recv_data[idx-5]);
        x_rot = parseFloat(recv_data[idx-4]);
        y_rot = parseFloat(recv_data[idx-3]);
        z_rot = parseFloat(recv_data[idx-2]);
        depth = parseFloat(recv_data[idx-1]);
        
        if (center_x != 0.0) {
            visibleHandler(i-1, true);
        }
        else{
            visibleHandler(i-1, false);
        }
        
        
        get_world_coords(i-1, center_x, center_y, depth);
        get_world_rotate(i-1, x_rot, y_rot, z_rot);
    }

}

async function render_video(){
    
    
    context.drawImage(videoElement, 0, 0, 1920, 1080);

    await requestAnimationFrame(render_video);
}

onLoad();