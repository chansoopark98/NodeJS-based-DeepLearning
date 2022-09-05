import * as camera_util from "./camera.js";
tf.ENV.set("WEBGL_CPU_FORWARD", true)
tf.setBackend('webgl');
// tf.setBackend('wsa')
console.log(tf.getBackend()); // tf backend 확인

const model = await tf.loadGraphModel('assets/pidnet/model.json');

const canvas = document.getElementById("render_area");
let context = canvas.getContext('2d');

// const videoElement = document.querySelector('video');
var videoElement = document.getElementById('video');

videoElement.addEventListener('canplaythrough', render_video);
console.log(videoElement.videoWidth, videoElement.videoHeight);
videoElement.width = 720;
videoElement.height = 1280;

// Initialize
camera_util.getCamera(videoElement);


async function render_video(){
    tf.engine().startScope()
    
    let date1 = new Date();
    
    const inputImageTensor = tf.expandDims(tf.cast(tf.browser.fromPixels(videoElement), 'float32'), 0);
    
    const resizedImage = tf.image.resizeBilinear(inputImageTensor, [512, 512]);
    
    
    // const output = await model.executeAsync(resizedImage);
    const output = await model.executeAsync(resizedImage);

    
    tf.dispose(inputImageTensor);
    tf.dispose(resizedImage);
    tf.dispose(output);

    var date2 = new Date();
    var diff = date2 - date1;
    console.log(diff);
    
 
    tf.engine().endScope()
    await requestAnimationFrame(render_video);
}

