tf.ENV.set("WEBGL_CPU_FORWARD", true)
tf.setBackend('webgl');
// tf.setBackend('wasm');
console.log(tf.getBackend()); // tf backend 확인

import * as camera_util from "./camera.js";
import { render_ar_video, switch_visible, get_world_coords } from "./three_test.js";

async function loadFaceLandmarkDetectionModel() {
    return faceLandmarksDetection
        .load(faceLandmarksDetection.SupportedPackages.mediapipeFacemesh,
            { maxFaces: 1 });
}
const model = await loadFaceLandmarkDetectionModel();


const canvas = document.getElementById("render_area");
let context = canvas.getContext('2d');
                
context.strokeStyle = "#00FFFF";
context.lineWidth = 4;
context.font = '48px serif';

context.fillStyle = "#000000";


var videoElement = document.getElementById('video');

videoElement.addEventListener('canplaythrough', render_video);
console.log(videoElement.videoWidth, videoElement.videoHeight);


videoElement.width = 480;
videoElement.height = 640;


// 페이지를 로드하면 실행 (구성요소들 초기화)
function onLoad() {
    console.log('on load')
    // canvas.width = width;
    // canvas.height = height;
    camera_util.getCamera(videoElement);
}


async function render_video(){
    // context.drawImage(videoElement, 0, 0, 720, 1280);  
    tf.engine().startScope()

    
    // const inputImageTensor = tf.expandDims(tf.cast(tf.browser.fromPixels(videoElement), 'float32'), 0);
    // const resizedImage = tf.image.resizeBilinear(inputImageTensor, [300, 300]);

       
    const predictions = await model.estimateFaces({
        input: videoElement
    });
    
    context.clearRect(0, 0, context.canvas.width, context.canvas.height);

    if(predictions.length > 0) {
        console.log(predictions[0].boundingBox);
        var topLeft = predictions[0].boundingBox.topLeft;
        var bottomRight = predictions[0].boundingBox.bottomRight;
        var xmin = (topLeft[0] / 480) * context.canvas.width;
        var ymin = (topLeft[1] / 640) * context.canvas.height;
        var width = ((bottomRight[0] - topLeft[0]) / 480) * context.canvas.width;
        var height = ((bottomRight[1] - topLeft[1])/ 640) * context.canvas.height;
        
        console.log(xmin,  ymin);
        context.strokeRect(xmin, ymin, width, height);

        context.fillText('detect', xmin, ymin);


        // draw mesh !
        // predictions.forEach(prediction => {
        //     const keypoints = prediction.scaledMesh;
        //     for (let i = 0; i < keypoints.length; i++) {
        //         const x = keypoints[i][0];
        //         const y = keypoints[i][1];

        //         context.beginPath();
        //         context.arc(x, y, 2, 0, 2 * Math.PI);
        //         context.fill();
        //     }
        // });
    
    }

    tf.engine().endScope()
    await requestAnimationFrame(render_video);
}

onLoad();