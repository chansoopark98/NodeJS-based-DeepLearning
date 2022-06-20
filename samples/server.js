var moment = require("./tcp_client.js");
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
var io = require('socket.io')(server);


app.set('view engine', 'ejs'); // 렌더링 엔진 모드를 ejs로 설정
app.set('views',  __dirname + '/views');    // ejs이 있는 폴더를 지정

app.get('/', (req, res) => {
    res.render(__dirname + "/camera.ejs");    // index.ejs을 사용자에게 전달
    // res.sendFile(__dirname + "/camera.html");
})

io.on('connection', (socket) => {   //연결이 들어오면 실행되는 이벤트
    var clients = [];

    socket.on('login', function(data) {
        var clientInfo = new Object();
        clientInfo.uid = data.uid;
        clientInfo.id = socket.id;
        clients.push(clientInfo);
        console.log(clientInfo)
    });
     
    // socket 변수에는 실행 시점에 연결한 상대와 연결된 소켓의 객체가 들어있다.
    console.log('html page is init');
    console.log(socket.id);

    //socket.emit으로 현재 연결한 상대에게 신호를 보낼 수 있다.
    socket.emit('usercount', io.engine.clientsCount);

    // on 함수로 이벤트를 정의해 신호를 수신할 수 있다.
    socket.on('message', (msg) => {
        //msg에는 클라이언트에서 전송한 매개변수가 들어온다. 이러한 매개변수의 수에는 제한이 없다.
        // console.log('Message received: ' + msg);
           
        // moment.writeData(msg);
        // io.emit으로 연결된 모든 소켓들에 신호를 보낼 수 있다.
        // io.emit('message', msg);
        
        
        moment.socket.write(clients.id + msg);
        var returned_data = moment.getRcvData();
        // console.log("tcp rcv data is ok : ", returned_data.split('')[0]);
    });
});

server.listen(server_port, function() {
  console.log( 'Express server listening on port ' + server.address().port );
});