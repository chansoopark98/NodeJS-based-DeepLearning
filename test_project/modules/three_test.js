import * as THREE from 'three';

//Video Texture
const video = document.getElementById( 'video' );
const texture = new THREE.VideoTexture( video );
texture.needsUpdate = true;
var material_video = new THREE.MeshBasicMaterial({ map: texture });


var scene = new THREE.Scene();
var camera = new THREE.PerspectiveCamera(45, 480 / 640, 1, 1000);

//var renderer = new THREE.WebGLRenderer();
var renderer = new THREE.WebGLRenderer( { canvas: render_area, alpha: true, preserveDrawingBuffer:true  } );
renderer.setSize(480, 640);
//document.body.appendChild(renderer.domElement);

const geometry = new THREE.BoxGeometry(10, 10, 10); // width, height, depth
const material = new THREE.MeshLambertMaterial({ color: 0x1ec876 });
const mesh = new THREE.Mesh(geometry, material_video);



mesh.position.set(0, 0, 0); // Optional, 0,0,0 is the default

const ambientLight = new THREE.AmbientLight(0x404040, 1.0);
var pointLight = new THREE.PointLight(0xffffff);
pointLight.position.set(100, 300, 200);
scene.add(pointLight);


scene.add(mesh);

camera.position.x = 0;
camera.position.y = 0;
camera.position.z = 100;


var vec = new THREE.Vector3(); // create once and reuse
// var pos = new THREE.Vector3(); // create once and reuse

function get_world_coords(center_x, center_y, roll, pitch, yaw, area, w, h){
  var pos = new THREE.Vector3(); // create once and reuse
  vec.set(
    ( center_x / 480 ) * 2 - 1,
    - ( center_y / 640 ) * 2 + 1,
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
  camera.rotation.x = roll;
  camera.rotation.y = pitch;
  // camera.rotation.z = yaw;
  
  var width = parseFloat(w);
  var height = parseFloat(h);
  
  var width_factor = width / height;
  var height_factor = height / width;
  // area 50000
  
  var scale_factor = parseInt(parseFloat(area) / 10000);
  
  if (scale_factor != 0){
    var width_scale = (1 + (0.2 * scale_factor)) * width_factor
    var height_scale = (1 +(0.2 * scale_factor)) * height_factor
    // console.log('width', width);
    // console.log('height', height);
    // console.log('scale_factor', scale_factor);
    // console.log('width_factor', width_factor);
    // console.log('height_factor', height_factor);
    // console.log('width_scale', width_scale);
    // console.log('height_scale', height_scale);
    
    mesh.scale.set(width_scale, height_scale, 1);
    
  }
  else{
    mesh.scale.set(1, 1, 1);
  }

  // mesh.scale.set(1.5, 1.5, 1);

}
  

var render = function(center_x, center_y) {

  // vec.set(
  //     ( center_x / 480 ) * 2 - 1,
  //     - ( center_y / 640 ) * 2 + 1,
  //     0.5 );

  // // console.log(vec);

  // vec.unproject( camera );

  // vec.sub( camera.position ).normalize();

  // var distance = - camera.position.z / vec.z;

  // pos.copy( camera.position ).add( vec.multiplyScalar( distance ) );


  // convert x,y to clip space; coords from top left, clockwise:
  // (-1,1), (1,1), (-1,-1), (1, -1)





  // requestAnimationFrame(render);
  renderer.render(scene, camera);
};

export {render, get_world_coords}
// render();
