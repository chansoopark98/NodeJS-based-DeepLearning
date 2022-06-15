#!/usr/bin/env node

// tcp port = 6666

// set tcp Client
var tcpClient = require('net')

/* 
psudo code

1. NodeJS tcp server -> Python tcp client
2. NodeJS tcp client <- Python tcp server
3. NodeJS web server open

python 에서도 socket을 ssl로 열어야함
wss 
*/


// set server 
let https = require('https');
let fs = require('fs');
let express = require('express');

let options = {
    key: fs.readFileSync('./privkey.pem'),
    cert: fs.readFileSync('./cert.pem'),
    requestCert: false,
    rejectUnauthorized: false
};

let app = express();
let port = process.env.PORT || 5555;
let server = https.createServer(options, app);

server.listen(port, function () {
    console.log( 'Express server listening on port ' + server.address().port );
} );

app.get("/", (req, res) => {
  res.sendFile(__dirname + "/camera.html");
});


