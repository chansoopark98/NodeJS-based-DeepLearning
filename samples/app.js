#!/usr/bin/env node



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



