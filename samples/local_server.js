var express = require('express');
var http = require('http');

var app = express();
var server = http.createServer(app);

app.get('/', function(req, res) {
    // res.send("Hello World!");
    res.render(__dirname + "/camera.ejs");    // index.ejs을 사용자에게 전달
});

server.listen(5555, 'localhost');
server.on('listening', function() {
    console.log('Express server started on port %s at %s', server.address().port, server.address().address);
});