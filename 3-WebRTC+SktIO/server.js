const http = require("http");
const express = require("express");
const io = require("socket.io");

// const { Server } = require("socket.io");
// const io = new Server(server);

const app = express();
const httpServer = http.createServer(app);
const ioServer = new io.Server(httpServer);

const port = 4000;

app.use(express.static(__dirname + "/app"));

// app.get('/', (req, res) => {
//     console.log(req);
//     res.sendFile(__dirname + '/index.html');
//   });

console.log(__dirname)

app.get((req, res) => {
    console.log(req);
    res.sendFile(__dirname + '/index.html');
  });

let broadcaster;
ioServer.on('connection', (socket) => {
    console.log('a user connected via WebSocket, socket ID: ' + socket.id);

    socket.on('broadcaster', ()=> {
        console.log('broadcaster event, broadcasting broadcaster ID!')
        broadcaster = socket.id; 
        socket.broadcast.emit("broadcaster");
    })

    socket.on("viewer", ()=> {
        console.log('viewer event, sending viewer ID to broadcaster')
        socket.to(broadcaster).emit("viewer", socket.id);
    })

    socket.on("disconnect", () => {
        socket.to(broadcaster).emit("disconnectPeer", socket.id);
    })

    socket.on("offer", (id, message) => {
        socket.to(id).emit("offer", socket.id, message);
    })

    socket.on("answer", (id, message) => {
        socket.to(id).emit("answer", socket.id, message);
    })

    socket.on("candidate", (id, message) => {
        socket.to(id).emit("candidate", socket.id, message);
    })

});

ioServer.sockets.on("error", (err) => {
    console.log(err)
});

httpServer.listen(port, () => {
console.log('http server is listening on *: '+port);
});