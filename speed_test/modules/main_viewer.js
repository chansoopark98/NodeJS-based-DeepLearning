import * as camera_util from "./camera.js";

tf.ENV.set("WEBGL_CPU_FORWARD", true)
tf.setBackend('webgl');
// tf.setBackend('wasm');
// tf.wasm.setThreadsCount(8);
console.log(tf.getBackend()); // tf backend 확인

const model = await tf.loadGraphModel('assets/segmentation/model.json');

// const model = await tf.loadLayersModel('assets/segmentation/model.json');

const canvas = document.getElementById("render_area");
let context = canvas.getContext('2d');

// const videoElement = document.querySelector('video');
var videoElement = document.getElementById('video');

videoElement.addEventListener('canplaythrough', render_video);
console.log(videoElement.videoWidth, videoElement.videoHeight);
videoElement.width = 720;
videoElement.height = 1280;

// Initialize
let idx = 0;
let frameIdx = 1;
let totalDuration = 0;
camera_util.getCamera(videoElement);
    

async function render_video(){
    tf.engine().startScope()
    
    let date1 = new Date();
    
    const inputImageTensor = tf.expandDims(tf.cast(tf.browser.fromPixels(videoElement), 'float32'), 0);
    const resizedImage = tf.image.resizeBilinear(inputImageTensor, [640, 360]);
    // const output = await model.executeAsync(resizedImage);
    // const output = await model.executeAsync(resizedImage);
    const output = await model.execute(resizedImage);

    tf.dispose(inputImageTensor);
    tf.dispose(resizedImage);
    tf.dispose(output);

    if (idx > 30) {
    var date2 = new Date();
    var diff = date2 - date1;
    totalDuration = totalDuration + diff;

    console.log(totalDuration / frameIdx);
    
    frameIdx = frameIdx + 1;
    }
    
    idx = idx + 1;

    tf.engine().endScope()
    await requestAnimationFrame(render_video);
}

