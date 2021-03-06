var net = require('net');
let rcv_data;
let hostname = '127.0.0.1';

function getConnection(connName){
  var client = net.connect({port: 7777, host:hostname}, function() {
    console.log(connName + ' Connected: ');
    console.log('   local = %s:%s', this.localAddress, this.localPort);
    console.log('   remote = %s:%s', this.remoteAddress, this.remotePort);
    // this.setTimeout(1000);
    this.setEncoding('utf8');
    this.on('data', function(data) {
      // console.log(connName + " From Server: " + data.toString());
      rcv_data = data;
      // this.end();
    });
    this.on('end', function() {
      console.log(connName + ' Client disconnected');
    });
    this.on('error', function(err) {
      console.log('Socket Error: ', JSON.stringify(err));
    });
    this.on('timeout', function() {
      console.log('Socket Timed Out');
    });
    this.on('close', function() {
      console.log('Socket Closed');
    });
  });
  return client;
}


function getRcvData(){
  console.log('get data');
  return rcv_data;
}

var socket = getConnection("test client");


function writeData(data){
  // console.log('write_Data', data);
  var success = !socket.write(data);
  console.log(success);
//   socket.send() or once
  if (!success){
    (function(data){
      socket.once('drain', function(){
        writeData(data);
      });
    })(socket, data);
  }
}

module.exports.writeData=writeData;
module.exports.getRcvData=getRcvData;
module.exports.socket=socket;

