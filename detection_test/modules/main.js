// import * as tf from "./@tensorflow/tfjs-node";


// import { load_model } from "../tf_test.js";

// https://www.tensorflow.org/js/guide/platform_environment?hl=ko // tf backend 변경 확인 방법
// tf.setBackend('wasm');
// tf.setBackend('webgl');
console.log(tf.getBackend()); // tf backend 확인

// import { loadGraphModel } from "@tensorflow/tfjs-node";
import * as camera_util from "./camera.js";

// const tf = require('@tensorflow/tfjs-node');
const model = await tf.loadGraphModel('assets/converted_tfjs/model.json');
// const model = await tf.loadLayersModel('assets/converted_tfjs/model.json');


// import * as tf from '@tensorflow/tfjs';


// 카메라 세팅 부분
let front_camera = false    // 전면 카메라 사용 유무
let width = 720;      // 해상도 (너비) 480
let height = 1280;    // 해상도 (높이) 640

// const canvas = document.createElement("canvas");
const canvas = document.getElementById("render_area");
let context = canvas.getContext('2d');

// const videoElement = document.querySelector('video');
var videoElement = document.getElementById('video');

videoElement.addEventListener('canplaythrough', render_video);
console.log(videoElement.videoWidth, videoElement.videoHeight);
videoElement.width = 720;
videoElement.height = 1280;
        

// 페이지를 로드하면 실행 (구성요소들 초기화)
function onLoad() {
    console.log('on load')
    // canvas.width = width;
    // canvas.height = height;
    camera_util.getCamera(videoElement);
}

function batched_nms(boxes, scores, idxs, iou_threshold, top_k){
    var max_corrdinate = tf.max(boxes, 0, false)
    var offsets = idxs * (max_corrdinate + 1);
}

async function render_video(){
    // context.drawImage(videoElement, 0, 0, 720, 1280);  
    tf.engine().startScope()

    

    const inputImageTensor = tf.expandDims(tf.cast(tf.browser.fromPixels(videoElement), 'float32'), 0);
    const resizedImage = tf.image.resizeBilinear(inputImageTensor, [300, 300]);
    const normalizedImage = tf.div(resizedImage, 255);
    // var output = model.predict(normalizedImage);
    // var output = await model.executeAsync(normalizedImage);
    // var output = model.predict(normalizedImage);
    var date1 = new Date();
    var output = model.execute(normalizedImage);
    

    var date2 = new Date();
    var diff = date2 - date1;
    console.log(diff);

    // var boxes = output.slice([0, 0], [-1, 4]);
    // var scores = output.slice([0, 4], [-1, 1]);
    // var labels = output.slice([0, 5], [-1, 1]);

    // scores = tf.squeeze(scores, 1)
    // labels = tf.squeeze(labels, 1)
    // // console.log(boxes);
    
    // boxes = boxes.arraySync();
    // scores = scores.arraySync();
    // labels = labels.arraySync();
    
    // var x_min = boxes[0][0];
    // var y_min = boxes[0][1];
    // var x_max = boxes[0][2];
    // var y_max = boxes[0][3];
    

    
    
    // var box_width = x_max - x_min;
    // var box_height = y_max - y_min;


    // // console.log(box_width);
    // // console.log(box_height);
    
    
    // // // # low_scoring_mask = scores > confidence_threshold
    // // var low_scoring_mask = tf.less(0.01, scores)
    
    // // // # boxes, scores, labels = tf.boolean_mask(boxes, low_scoring_mask), tf.boolean_mask(scores, low_scoring_mask), tf.boolean_mask(labels, low_scoring_mask)
    // // boxes = await tf.booleanMaskAsync(boxes, low_scoring_mask);
    // // scores = await tf.booleanMaskAsync(scores, low_scoring_mask);
    // // labels = await tf.booleanMaskAsync(labels, low_scoring_mask);
    
    // // # keep  = batched_nms(boxes, scores, labels, iou_threshold, top_k)

    // // # boxes, scores, labels = tf.gather(boxes, keep), tf.gather(scores, keep), tf.gather(labels, keep)
    // console.log(canvas.width);
    // context.beginPath();
    // context.rect(x_min * canvas.width , y_min * canvas.height, box_width * canvas.width, box_height * canvas.height);
    // context.stroke();
    tf.engine().endScope()
    await requestAnimationFrame(render_video);
}

onLoad();