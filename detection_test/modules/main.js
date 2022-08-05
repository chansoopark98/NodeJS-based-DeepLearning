tf.ENV.set("WEBGL_CPU_FORWARD", true)
tf.setBackend('webgl');
// tf.setBackend('wasm');
console.log(tf.getBackend()); // tf backend 확인

import * as camera_util from "./camera.js";

tf.ready().then(() => {
});

const model = await tf.loadGraphModel('assets/converted_tfjs/model.json');
// const warmupResult = model.predict(tf.zeros([1,300,300,3]));
// warmupResult.dataSync();
// warmupResult.dispose();


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

    
    const date1 = new Date();
    
    // const logits = tf.tidy(() => {
    //     const inputImageTensor = tf.expandDims(tf.cast(tf.browser.fromPixels(videoElement), 'float32'), 0);
    //     const resizedImage = tf.image.resizeBilinear(inputImageTensor, [300, 300]);
    //     const normalizedImage = tf.div(resizedImage, 255);
    //     // var output = model.predict(normalizedImage);
    //     var output = await model.executeAsync(normalizedImage);
    //     // var output = model.predict(normalizedImage); // [1, 8732, 25]
        
    //     // batch_boxes = detections[:, :, classes:]
    
    //     console.log(output);
    //     output.dataSync();
    //     output.dispose();
    //     return output
    //   });

    const inputImageTensor = tf.expandDims(tf.cast(tf.browser.fromPixels(videoElement), 'float32'), 0);
    const resizedImage = tf.image.resizeBilinear(inputImageTensor, [300, 300]);
    const normalizedImage = tf.div(resizedImage, 255);
    // var output = model.predict(normalizedImage);
    var output = await model.executeAsync(normalizedImage);


    output = tf.squeeze(output, 0); // [1, 1, 6] -> [1, 6]
    
                
    context.strokeStyle = "#00FFFF";
    context.lineWidth = 4;
    context.font = '48px serif';

    context.fillStyle = "#000000";
    
    context.clearRect(0, 0, context.canvas.width, context.canvas.height);
    if (output.shape[0] >= 1){
        var boxes = output.slice([0, 0], [-1, 4]); // [1, 4]
        var scores = output.slice([0, 4], [-1, 1]); // [1, 1]
        var labels = output.slice([0, 5], [-1, 1]); // [1, 1]
        
        // console.log(scores.dataSync(), labels.dataSync());
        var calc_boxes = boxes.dataSync();
        // console.log(calc_boxes.length); // [1, 2, 6]
        var target_loop = calc_boxes.length/2
        var detected_labels = labels.dataSync();

        for (let i=1; i<=target_loop; i++){
            console.log(detected_labels);
            var idx = i * 4;
            var x_min = calc_boxes[idx-4] * context.canvas.width;
            var y_min = calc_boxes[idx-3] * context.canvas.height;
            var x_max = calc_boxes[idx-2] * context.canvas.width;
            var y_max = calc_boxes[idx-1] * context.canvas.height;    
            var width = x_max- x_min;
            var height = y_max - y_min;
        

            context.strokeRect(x_min, y_min, width, height);

            // const font = "16px sans-serif";
            // const textWidth = context.measureText(detected_labels[i-1]).width;
            // const textHeight = parseInt(font, 10); // base 10
            // context.fillRect(x_min, y_min, textWidth + 4, textHeight + 4);

            context.fillText(detected_labels[i-1], x_min, y_min);
        }
        
    
        
    }
    



    var date2 = new Date();
    var diff = date2 - date1;
    console.log(diff);

 
    tf.engine().endScope()
    await requestAnimationFrame(render_video);
}

onLoad();