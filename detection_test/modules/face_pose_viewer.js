tf.ENV.set("WEBGL_CPU_FORWARD", true)
tf.setBackend('webgl');
// tf.setBackend('wasm');
console.log(tf.getBackend()); // tf backend 확인

import * as camera_util from "./camera.js";
import { render_ar_video, switch_visible, get_world_coords, get_world_rotate } from "./face_pose_ar.js";

var webSocket = new WebSocket("wss://park-tdl.tspxr.ml:7777");

// 이미지를 저장하기 위한 canvas 생성


const canvas = document.getElementById("render_area");
canvas.width=1920;
canvas.height=1080;



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
    var recv_data = message.data.split(',');
    var center_x = parseFloat(recv_data[0]);
    var center_y = parseFloat(recv_data[1]);
    var x_rot = parseFloat(recv_data[2]);
    var y_rot = parseFloat(recv_data[3]);
    var z_rot = parseFloat(recv_data[4]);
    console.log(center_x, center_y)
    get_world_coords(center_x, center_y);
    get_world_rotate(x_rot, y_rot, z_rot);
    
    // get_world_coords
    // console.log(recv_data);
}

async function render_video(){
    console.log('draw image');
    context.drawImage(videoElement, 0, 0, 1920, 1080);

    await requestAnimationFrame(render_video);
}

onLoad();