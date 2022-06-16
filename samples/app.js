#!/usr/bin/env node

// tcp port = 6666

// set tcp Client

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
// app.use(express.static('sampels'));
// app.use('/js', express.static(__dirname + '/js'));
app.use('/samples', express.static(__dirname));

console.log(__dirname)
let port = process.env.PORT || 5555;
let server = https.createServer(options, app);

server.listen(port, function () {
    console.log( 'Express server listening on port ' + server.address().port );
} );

app.get("/", (req, res) => {
  // var test = require('./tcp_client') >> 이렇게하면 외부 .js 파일 호출 가능
  res.sendFile(__dirname + "/camera.html");
});


