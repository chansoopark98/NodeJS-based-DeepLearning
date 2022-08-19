import { GLTFLoader } from '../gltf/examples/jsm/loaders/GLTFLoader.js';
import * as THREE from '../build/three.module.js'

const loader = new GLTFLoader();

var originalVideo = document.getElementById('video');
originalVideo.addEventListener('canplaythrough', render_ar_video);

var camera_width = 1920; // 480
var camera_height = 1080; // 640


var scene = new THREE.Scene();
var camera = new THREE.PerspectiveCamera(45, camera_width / camera_height, 1, 1000);

//var renderer = new THREE.WebGLRenderer();
var renderer = new THREE.WebGLRenderer( { canvas: render_ar, alpha: true, preserveDrawingBuffer:true  } );
renderer.setSize(camera_width, camera_height);
var factor = 1.0;
renderer.setPixelRatio(window.devicePixelRatio * factor)
renderer.outputEncoding = THREE.sRGBEncoding;


var pointLight = new THREE.PointLight(0xffffff);
pointLight.position.set(100, 300, 200);
scene.add(pointLight);

camera.position.x = 0;
camera.position.y = 0;
camera.position.z = 120;


loader.load('assets/Anna_OBJ/trump.gltf', function ( gltf ) {
    gltf.scene.scale.set(15, 15, 1 );			   
    gltf.scene.position.set(0, 0, 0);
    gltf.scene.visible=true;
 
    scene.add(gltf.scene);

}, undefined, function ( error ) {
	console.error( error );
} );

var vec = new THREE.Vector3(); // create once and reuse

function get_world_coords(center_x, center_y){

  var pos = new THREE.Vector3(); // create once and reuse
  vec.set(
    ( center_x / camera_width ) * 2 - 1,
    - ( center_y / camera_height ) * 2 + 1,
    0.5 );

  vec.unproject(camera);

  vec.sub(camera.position).normalize();

  var distance = - camera.position.z / vec.z;
  // pos.copy( camera.position ).add( vec.multiplyScalar( distance ) );
  var value = vec.multiplyScalar( distance );
  // console.log(value);
  // console.log(center_x, center_y, pos);
  camera.position.x = -(pos.x + value.x);
  camera.position.y = -(pos.y + value.y);

  
}


function get_world_rotate(x_rot, y_rot, z_rot){  
    // camera.position.x = radius * Math.cos( angle );  
    // camera.position.z = radius * Math.sin( angle );

    // camera.rotation.x = x_rot * 15
    camera.rotation.y = -y_rot * 30;
    // camera.rotation.z = z_rot
  }

function switch_visible(visible_flag){
  mesh.visible = visible_flag;
}
  

// var render = function(visible_flag) {
//   mesh.visible=visible_flag;
//   // video_img.src = 'https://park-tdl.tspxr.ml:4447/stream?src=0';
  
//   renderer.render(scene, camera);
//   requestAnimationFrame(render);
// };

async function render_ar_video(){
  
//   console.log('render!')
  renderer.render(scene, camera);
  await requestAnimationFrame(render_ar_video);
  // setTimeout(render_ar_video, 1)
}

export {render_ar_video, switch_visible, get_world_coords, get_world_rotate};
// render();
