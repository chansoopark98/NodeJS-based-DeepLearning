/**
 *  @author XHI-NM <jeong.chiseo@tsp-xr.com>
 *  @description
 *  Connect server and  using websockets
 */


import * as CamUtil from "./camera.js";
import { render } from "./three_test.js";


 
class WebDetector {
    constructor(baseVideo, address, port, useFlag=false) {
        
        this.baseVideo = baseVideo;
        this.address = address;
        this.port = port;
        this.maxFPS = 30;
        console.log(this.baseVideo);
        this.videoWidth = this.baseVideo.videoWidth;
        this.videoHeight = this.baseVideo.videoHeight;
        this.captureCanvas = document.createElement("canvas");
        
        this.captureCanvas.width = this.videoWidth;
        this.captureCanvas.height = this.videoHeight;
        this.captureContext = this.captureCanvas.getContext("2d");
        
        this.startButton = document.getElementById("start-button");
        this.startButton.onclick = this.process;
 
        this.useFlag = useFlag;
        this.msgFlag = "$$M";
        this.imgFlag = "$$I";
        this.requestFlag = "$$G";
        this.failedFlag = "$$F";
        
        
        this.clientId = Math.random().toString(16).substring(2,11);
        this.clientId += ',';
         
 
        this.connectServer().then((connection) => {
             if (connection) {
                 
             }
         })
     }
     
     
    async connectServer() {
        return new Promise((resolve, reject) => {
            //const wssAddress = `wss://${this.address}:${this.port}`;
            const wssAddress = `ws://${this.address}:${this.port}`;
            console.log(wssAddress);
            this.wss = new WebSocket(wssAddress)
 
            this.wss.onmessage = (event) => {
                let rawData = JSON.parse(event.data);
                 
                if (this.useFlag) {
                     let flag = rawData[0];
                     let data = rawData[1];
 
                     switch(flag) {
                         case this.msgFlag:
                             console.log(`Server : ${data}`);
                             break;
                         case this.requestFlag:
                             
                             break;
                     }
                 }
             }
             this.wss.onopen = () => {
                 console.log("connect successfully!")
                 resolve(true);
             }

            //  this.wss.setInterval = setInterval(() => { // ?초마다 클라이언트로 메시지 전송
            //     if (this.wss.readyState === this.wss.OPEN) {
            //         this.process()
            //         }
            //     }, 150); 

             this.wss.onclose = () => {
                 console.log("disconneted")
                 reject(false);
             }
             this.wss.onerror = () => {
                 console.error("error occured! failed to connect server.")
                 reject(false);
             }
         });
     }
 
     sender(imageBase64) {
        console.log('sender');
         let imageData = {
             "data": imageBase64
         }
 
         if (this.useFlag) {
             imageData["flag"] = this.imgFlag;
         }
 
         try {
             this.wss.send(this.clientId + imageBase64);
         } catch (error) {
             console.error(error);
         }
     }
 
     process() {
        console.log('process');
         try {
             this.captureContext.drawImage(this.baseVideo, 0, 0, this.videoWidth, this.videoHeight);
             let imageBase64 = this.captureCanvas.toDataURL("image/jpeg", 0.3)
             this.sender(imageBase64);
             return true;
         } catch (error) {
             console.error(error);
             return false;
         }
     }

 }

 
 window.onload = () => {
    console.log('load index.js');
    // const videoElement = document.querySelector("#base-video");
    const videoElement = document.getElementById("base-video");
    console.log(videoElement);
    const videoStream = CamUtil.getCamera(videoElement);
    const hostAddress = "127.0.0.1";
    const hostPort = "7777";
    
    const webServer = new WebDetector(videoElement, hostAddress, hostPort, false)


    
 }