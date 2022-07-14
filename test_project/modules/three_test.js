import * as THREE from 'three';

var scene = new THREE.Scene();
// w: 480 h: 640
var camera = new THREE.PerspectiveCamera(45, 480 / 640, 1, 1000);

//var renderer = new THREE.WebGLRenderer();
var renderer = new THREE.WebGLRenderer( { canvas: render_area, alpha: true, preserveDrawingBuffer:true  } );
renderer.setSize(480, 640);
//document.body.appendChild(renderer.domElement);

var geometry = new THREE.SphereGeometry(3, 15, 32, 16, Math.PI * 2, 0, Math.PI * 2);

var material1 = new THREE.MeshBasicMaterial();
var material2 = new THREE.MeshBasicMaterial();
var sphere = [new THREE.Mesh(geometry, material1), new THREE.Mesh(geometry, material1), new THREE.Mesh(geometry, material2)];

sphere[0].position.set(1, 1, 10);
sphere[0].rotation.set(10, 10, 10);

scene.add(sphere[0]);

camera.position.x = 10;
camera.position.y = -20;
camera.position.z = 100;



var hex = "0x" + "000000".replace(/0/g, function() {
  return (~~(Math.random() * 16)).toString(16);
});
sphere[0].material.color.setHex(hex);

hex = "0x" + "000000".replace(/0/g, function() {
  return (~~(Math.random() * 16)).toString(16);
});
sphere[2].material.color.setHex(hex);


var render = function() {
  requestAnimationFrame(render);
  renderer.render(scene, camera);
};

export {render}
// render();
