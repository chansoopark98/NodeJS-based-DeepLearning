/**
 *  @author XHI-NM <jeong.chiseo@tsp-xr.com>
 *  @description
 *  Camera function for get rear camerea with general wide-angle
 */

 console.log('load camera.js');
 
 let isIOS = null;
 let isMobile = null;

 

 function getLogTitle(text) {
     let base = "======================================";
     return (base + `\n${text}\n` +base);
 }
 
 function getUserAgent() {
     return navigator.userAgent.toLowerCase();
 }
 
 function getCameraSpecification() {
     return new Promise(async (resolve, reject) => {
         let cameraList = [];
         let focusDistanceMax = 0;
 
         if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
             const deviceList = await navigator.mediaDevices.enumerateDevices();
     
             for (let i = 0; i < deviceList.length; i++) {
                 const device = deviceList[i];
     
                 if (device.kind === "videoinput") {
                     const deviceId = device.deviceId;
     
                     const constraints = {
                         audio: false,
                         video: {
                             deviceId: deviceId
                         }
                     };
     
                     const stream = await navigator.mediaDevices.getUserMedia(constraints);
                     stream.getVideoTracks().forEach(track => {
                         const capabilities = track.getCapabilities();
     
                         if (capabilities.facingMode[0] == "environment") {
                             console.log(getLogTitle(device.label));
                             console.log(device);
                             console.log(capabilities);
 
                             let fd = capabilities.focusDistance;
 
                             if (fd.min > 0){
                                 if (focusDistanceMax < fd.max) {
                                     focusDistanceMax = fd.max;
                                     cameraList.unshift(deviceId);
                                 } else  {
                                     cameraList.push(deviceId);
                                 }
                                 
                             }
                         }
                     })
                     stream.getTracks().forEach(track => {
                         track.stop();
                     });
                 }
             }
             resolve(cameraList);
         } else {
             console.log("This device does not support web camera.");
             reject(cameraList);
         }
     });
 }
 
 function openCamera(baseVideo, deviceId) {
    console.log('openCamera');
        
     return new Promise((reserve, reject) => {
         let video = {
             width: 1280,
             height: 960
         }
     
         if (deviceId == "ios") {
             video.facingMode = "environment";
         } else {
             video.deviceId = deviceId;
         }
     
         let constraints = {
             audio: false,
             video: video
         };
         
        //  console.log('focal lenght?', navigator.mediaDevices.getCameraSpecification());

         navigator.mediaDevices.getUserMedia(constraints).then(stream => {
             stream.getVideoTracks().forEach(track => {
                 
                 console.log(track);
                 console.log(track.getSettings());
             });
             
             baseVideo.srcObject = stream;
             // Original player
             baseVideo.addEventListener("loadedmetadata", () => {
                 console.log('play');
                 baseVideo.play();
                 reserve(true, stream);
             });
         }).catch("Open camera failed!");
     })
 }
 
 function getCamera(baseVideo) {
     const userAgent = getUserAgent();
 
     if (userAgent.match("iphone") || userAgent.match("ipad") || userAgent.match("ipod") || userAgent.match("mac")) {
         isIOS = true;
         isMobile = true;
         if (!userAgent.match("safari") || userAgent.match("naver") || userAgent.match("twitter")) {
             isIOS = false;
         }
     } else {
         isMobile = userAgent.match("Android") || userAgent.match("mobile");
     }
 
     getCameraSpecification().then((cameraList) => {
         let cameraId = "";
 
         if (cameraList.length > 0) {
             cameraId = cameraList[0];
         }
         else if (isIOS) {
             cameraId = "ios";
         }
 
         openCamera(baseVideo, cameraId).then((camAct, stream) => {
             if (camAct) {
                 return stream
             }
         })
     });
 }
 
 export {getCameraSpecification, getCamera}