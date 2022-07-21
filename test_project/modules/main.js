import { render, get_world_coords } from "./three_test.js";
import * as camera_util from "./camera.js";

var webSocket = new WebSocket("wss://park-tdl.tspxr.ml:7777");
// var webSocket = new WebSocket("ws://127.0.0.1:7777");

// 카메라 세팅 부분
let front_camera = false    // 전면 카메라 사용 유무
let width = 720;      // 해상도 (너비) 480
let height = 1280;    // 해상도 (높이) 640

// var render_canvas = document.getElementById("render_area");
// render_canvas.width = width;
// render_canvas.height = height;
const canvas = document.createElement("canvas");
var startButton = document.getElementById("start-button");
startButton.onclick = startEvent;
var visible_flag = false;
let context = canvas.getContext('2d');
var center_x = 0;
var center_y = 0;
var tmp_center_x = 0;
var tmp_center_y = 0;
var roll = 0;
var pitch = 0;
var yaw = 0;
var area = 0;
var w = 0;
var h = 0;

// const videoElement = document.querySelector('video');
var videoElement = document.getElementById('video');
videoElement.addEventListener('canplaythrough', render_video);
console.log(videoElement.videoWidth, videoElement.videoHeight);
videoElement.width = 720;
videoElement.height = 1280;


function startEvent() {
    visible_flag = !visible_flag;
    console.log(visible_flag);
}

webSocket.interval = setInterval(() => { // ?초마다 클라이언트로 메시지 전송
    if (webSocket.readyState === webSocket.OPEN) {
        if (visible_flag == true) {
            var sendData = canvas.toDataURL('image/jpeg', 0.5)
            webSocket.send(sendData.split(",")[1]);
        }
    }
}, 100);

webSocket.onmessage = function(message){
    var recv_data = message.data.split(',');
    center_x = recv_data[0];
    center_y = recv_data[1];
    roll = recv_data[2];
    pitch = recv_data[3];
    yaw = recv_data[4];
    area = recv_data[5];
    w = recv_data[6];
    h = recv_data[7];
    console.log(center_x);
    
    // x축 세팅, 이전 프레임의 x축보다 10픽셀 이하로 차이나는 경우
    if (Math.abs(center_x-tmp_center_x) > 10){
        console.log('x축 100 이하');
        tmp_center_x = center_x;
        }
    if (Math.abs(center_y-tmp_center_y) > 10){
            console.log('y축 100 이하');
            tmp_center_y = center_y;
            }

    get_world_coords(tmp_center_x, tmp_center_y, roll, pitch, yaw, area, w, h)
};
        

// 페이지를 로드하면 실행 (구성요소들 초기화)
function onLoad() {
    console.log('on load')
    canvas.width = width;
    canvas.height = height;
    camera_util.getCamera(videoElement);
    // const streamImg = document.createElement("img");
    // streamImg.src = "https://park-tdl.tspxr.ml:4447/stream?src=0";
    // streamImg.id = 'test';
    // streamImg.style = "display: none;";
}

async function render_video(){
    context.drawImage(videoElement, 0, 0, 720, 1280);  
    render(visible_flag);
    await requestAnimationFrame(render_video)
}

onLoad();