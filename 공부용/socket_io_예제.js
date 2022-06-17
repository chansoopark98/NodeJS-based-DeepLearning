    
//현재 연결되어있는 클라이언트 소켓에 전달
socket.emit("이벤트이름", {data:"현재 연결되어 있는 클라이언트"});

// 나를 제외한 다른 클라이언트에게 전달
socket.broadcast.emit("이벤트이름", {data:"나를 제외한 다른 클라이언트"});

// 특정 소켓 클라이언트에게 전달 
socketServer.sockets().emit("이벤트 이름", {data:"특정 소켓 클라이언트에게 전달"});
// 출처: https://hoony-gunputer.tistory.com/entry/socket-io사용하기 [후니의  컴퓨터:티스토리]
