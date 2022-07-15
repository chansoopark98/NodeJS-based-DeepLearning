import { render, get_world_coords } from "./three_test.js";

console.log('main.js init');
// var webSocket = new WebSocket("wss://park-tdl.tspxr.ml:7777");
var webSocket = new WebSocket("ws://127.0.0.1:7777");

console.log('ws');

// 카메라 세팅 부분
let front_camera = false    // 전면 카메라 사용 유무
let width = 480;     // 해상도 (너비)
let height = 640;    // 해상도 (높이)
let camera_resolution = [width, height];     // 해상도
const fps = 30;      //FPS
const capture_time = 1000;  // 캡쳐 시간

// var render_canvas = document.getElementById("render_area");
// render_canvas.width = width;
// render_canvas.height = height;
const canvas = document.createElement("canvas");
var startButton = document.getElementById("start-button");
startButton.onclick = startEvent;
let context = canvas.getContext('2d');
var center_x = 0;
var center_y = 0;
var roll = 0;
var pitch = 0;
var yaw = 0;
var area = 0;
var w = 0;
var h = 0;
const videoElement = document.querySelector('video');
videoElement.addEventListener('canplaythrough', render_video);


function startEvent() {
    webSocket.interval = setInterval(() => { // ?초마다 클라이언트로 메시지 전송
        if (webSocket.readyState === webSocket.OPEN) {
            var sendData = canvas.toDataURL('image/jpeg', 0.3)
            webSocket.send(sendData.split(",")[1]);
            }
        }, 150);        
}

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
    // console.log(center_x, center_y);
    get_world_coords(center_x, center_y, roll, pitch, yaw, area, w, h)
};
        

// 페이지를 로드하면 실행 (구성요소들 초기화)
function onLoad() {
    console.log('on load')
    if (navigator.platform.indexOf('arm') !== -1 || navigator.platform.indexOf('aarch') !== -1) {
        [width, height] = [height, width]
    }
    video.width = width;
    video.height = height;
    canvas.width = width;
    canvas.height = height;
    
    // canvas.style.visibility = 'hidden';
    // canvas.style.display='none';
    stream();
    // video.style.visibility = 'hidden';
}

// 웹에서 카메라 사용을 위한 스트림 생성
function stream() {
    let constraints = {
        audio: false,
        video: video
    };
    navigator.mediaDevices.getUserMedia(constraints).then(stream => {
        stream.getVideoTracks().forEach(track => {
            //console.log(track);
            console.log(track.getSettings());
        });

        video.srcObject = stream;
        video.addEventListener("loadedmetadata", () => {
            video.play();
            reserve(true, stream);
        });
    }).catch("Open camera failed!");
}

async function render_video(){
    context.drawImage(videoElement, 0, 0);  
    render(center_x, center_y, roll, pitch, yaw);
    await requestAnimationFrame(render_video)
}

onLoad();