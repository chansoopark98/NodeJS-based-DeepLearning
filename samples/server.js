var app = require('express')();
let fs = require('fs');
let options = {
    key: fs.readFileSync('./privkey.pem'),
    cert: fs.readFileSync('./cert.pem'),
    requestCert: false,
    rejectUnauthorized: false
};
var server_port = 5555;
var server = require('https').createServer(options, app);

app.set('view engine', 'ejs'); // 렌더링 엔진 모드를 ejs로 설정
app.set('views',  __dirname + '/views');    // ejs이 있는 폴더를 지정

app.get('/', (req, res) => {
    res.render(__dirname + "/camera.ejs");    // index.ejs을 사용자에게 전달
})

server.listen(server_port, function() {
  console.log( 'Express server listening on port ' + server.address().port );
});