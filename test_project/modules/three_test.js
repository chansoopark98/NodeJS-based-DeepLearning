import * as THREE from 'three';

var camera_width = 720; // 480
var camera_height = 1280; // 640
//Video Texture

// const video = document.getElementById( 'video' );
// const texture = new THREE.VideoTexture( video );

{/* <img id="test" src="https://park-tdl.tspxr.ml:4447/stream?src=0" crossorigin="anonymous"></img> */}

{/* <video id="test" src="https://park-tdl.tspxr.ml:4447/video?src=0"  crossorigin="anonymous"  */}
                  // autoplay="autoplay"></video>


// const video = document.createElement('video');


const video_img = document.getElementById( 'test' );
video_img.src = "https://park-tdl.tspxr.ml:4447/video?src=0";
video_img.crossOrigin="anonymous";
video_img.autoplay=true;
video_img.loop=true;



const texture = new THREE.VideoTexture(video_img);
texture.generateMipmaps = false;
texture.minFilter = THREE.NearestFilter;
texture.magFilter = THREE.NearestFilter;
texture.format = THREE.RGBAFormat;



// texture.setCrossOrigin("anonymous");



// const textureLoader = new THREE.TextureLoader();
// textureLoader.crossOrigin = "Anonymous"
// 'https://park-tdl.tspxr.ml:4447/stream?src=0'
// const texture = textureLoader.load('https://park-tdl.tspxr.ml:4447/stream?src=0');

// const texture = new THREE.Texture(video_img);




texture.needsUpdate = true;
const material_video = new THREE.MeshBasicMaterial({ map: texture , }); //side: THREE.FrontSide
const mat2 = new THREE.MeshBasicMaterial({color: 0x000000});
const mat3 = new THREE.MeshBasicMaterial({color: 0x000000});
const mat4 = new THREE.MeshBasicMaterial({color: 0x000000});
const mat5 = new THREE.MeshBasicMaterial({color: 0x000000});
const mat6 = new THREE.MeshBasicMaterial({color: 0x000000})
var materials = [mat2, mat3, mat4, mat5, material_video, mat6]

var scene = new THREE.Scene();
var camera = new THREE.PerspectiveCamera(45, camera_width / camera_height, 1, 1000);

//var renderer = new THREE.WebGLRenderer();
var renderer = new THREE.WebGLRenderer( { canvas: render_area, alpha: true, preserveDrawingBuffer:true  } );
renderer.setSize(camera_width, camera_height);
//document.body.appendChild(renderer.domElement);

const geometry = new THREE.BoxGeometry(10, 10, 10); // width, height, depth
const material = new THREE.MeshLambertMaterial({ color: 0x1ec876 });
const mesh = new THREE.Mesh(geometry, materials);



mesh.position.set(0, 0, 0); // Optional, 0,0,0 is the default

const ambientLight = new THREE.AmbientLight(0x404040, 1.0);
var pointLight = new THREE.PointLight(0xffffff);
pointLight.position.set(100, 300, 200);
scene.add(pointLight);


scene.add(mesh);

camera.position.x = 0;
camera.position.y = 0;
camera.position.z = 120;


var vec = new THREE.Vector3(); // create once and reuse
// var pos = new THREE.Vector3(); // create once and reuse

function get_world_coords(center_x, center_y, roll, pitch, yaw, area, w, h){
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
  camera.rotation.x = 0.1;
  console.log(camera.rotation.x);
  // camera.rotation.y = pitch ;
  // camera.rotation.z = yaw;
  
  mesh.scale.set(1.33, 1, 2);
}
  

var render = function(visible_flag) {
  mesh.visible=visible_flag;
  // video_img.src = 'https://park-tdl.tspxr.ml:4447/stream?src=0';
  
  renderer.render(scene, camera);
  requestAnimationFrame(render);
};

export {render, get_world_coords}
// render();
