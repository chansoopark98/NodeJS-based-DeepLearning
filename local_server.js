var express = require('express');
var http = require('http');

var app = express();

app.engine('html', require('ejs').renderFile);
app.set('view engine', 'html');

// app.use(
//     '/build/',
//     express.static(path.join(
//       __dirname,
//       'node_modules/three/build'
//     ))
//   )

app.use('/build', express.static('./node_modules/three/build'));
app.use('/modules', express.static(__dirname + '/modules'));

var server = http.createServer(app);


app.get('/', function(req, res) {
    // res.send("Hello World!");
    // res.sendFile(__dirname + "/demo.html");
    res.render(__dirname + "/demo.html");    // index.ejs을 사용자에게 전달
});

server.listen(5556, 'localhost');
server.on('listening', function() {
    console.log('Express server started on port %s at %s', server.address().port, server.address().address);
});