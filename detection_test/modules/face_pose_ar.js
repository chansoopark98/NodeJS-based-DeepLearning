/*
  2022 Kintex Face pose detection demo
*/

// Import modules
import { GLTFLoader } from '../gltf/examples/jsm/loaders/GLTFLoader.js';
import * as THREE from '../build/three.module.js'

// Set global variable
var model; // GLTF 모델
var secondModel;
var factor = 1.0; // 비디오 퀄리티 팩터 (0 ~ 1)
var camera_width = 1920; // 렌더링할 캔버스 너비
var camera_height = 1080; // 렌더링할 캔버스 높이

// Configurate GLTF loader
const loader = new GLTFLoader();
// Get video element
const originalVideo = document.getElementById('video');
// Set video element listener (Async fuction)
originalVideo.addEventListener('canplaythrough', render_ar_video);

// Three.js 기본 설정
var scene = new THREE.Scene();
var camera = new THREE.PerspectiveCamera(45, camera_width / camera_height, 1, 1000);
var renderer = new THREE.WebGLRenderer({
    canvas: render_ar,
    alpha: true, preserveDrawingBuffer: true
});
renderer.setSize(camera_width, camera_height);

renderer.setPixelRatio(window.devicePixelRatio * factor)
renderer.outputEncoding = THREE.sRGBEncoding;

var pointLight = new THREE.PointLight(0xffffff);
pointLight.position.set(100, 300, 200);
scene.add(pointLight);

camera.position.x = 0;
camera.position.y = 0;
camera.position.z = 10;

var test_models = [];

loader.load('assets/Anna_OBJ/trump.gltf', function ( gltf ) {
    gltf.scene.scale.set(1, 1, 1 );			   
    gltf.scene.position.set(0, 0, 0);
    gltf.scene.visible=false;

    
    model = gltf.scene;
    test_models.push(model);
    scene.add(gltf.scene);

}, undefined, function ( error ) {
	console.error( error );
} );


loader.load('assets/Anna_OBJ/trump.gltf', function ( gltf ) {
    gltf.scene.scale.set(1, 1, 1 );			   
    gltf.scene.position.set(0, 0, 0);
    gltf.scene.visible = false;

    secondModel = gltf.scene;
    test_models.push(secondModel);
    scene.add(secondModel);

}, undefined, function ( error ) {
	console.error( error );
} );




var vec = new THREE.Vector3(); // create once and reuse

function visibleHandler(idx, bool){
    test_models[idx].visible = bool;
}


function get_world_coords(idx, center_x, center_y, depth){
    
    
    center_x = center_x - (250 * model.rotation.y);
    
    center_y = center_y + 170;
    var pos = new THREE.Vector3(); // create once and reuse
    vec.set(
        (( center_x / camera_width ) * 2 - 1).toFixed(4),
        (- ( center_y / camera_height ) * 2 + 1).toFixed(4),
        0.5 );

    vec.unproject(camera);
    
    vec.sub(camera.position).normalize();
    
    var distance = - camera.position.z / vec.z;
    
    var value = vec.multiplyScalar( distance.toFixed(4) );
  
    if (idx == 0) {
        model.position.z = -depth.toFixed(3);
        model.position.x = (pos.x + value.x).toFixed(3);
        model.position.y = (pos.y + value.y).toFixed(3);
        console.log(center_x, center_y);
        console.log(model.position);
    }
    else{
        secondModel.position.x = (pos.x + value.x);
        secondModel.position.y = (pos.y + value.y);
    }
    
    
}


function get_world_rotate(idx, x_rot, y_rot, z_rot){  

    if (idx == 0) {
        model.rotation.x = (-x_rot * 15).toFixed(2);
        model.rotation.y = (y_rot * 30).toFixed(2);

        // console.log(model.rotation);
    }
    else{
        secondModel.rotation.x = -x_rot * 15;
        secondModel.rotation.y = y_rot * 30;
    }
    
  }

function switch_visible(visible_flag){
  mesh.visible = visible_flag;
}

async function render_ar_video(){
  renderer.render(scene, camera);
  await requestAnimationFrame(render_ar_video);
}

export {render_ar_video, switch_visible, get_world_coords, get_world_rotate, visibleHandler};
