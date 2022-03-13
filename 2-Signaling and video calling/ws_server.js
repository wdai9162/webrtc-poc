"use strcit";

const http = require('http');
const { connection } = require('websocket');
//const fs = require('fs');
//const { server } = require('websocket');
const WebSocketServer = require('websocket').server;


var connectionArray=[];
var nextID = Date.now();
var appendToMakeUnique = 1;

//Create a HTTP server ---> https://nodejs.org/api/http.html#class-httpserver
const httpServer = http.createServer((req,res) => {
    console.log((new Date()) + ": Received request for " + req.url);
    res.writeHead(404);
    res.end()
});

//HTTP server listens on TCP port 8000
httpServer.listen(8000, ()=> {
    console.log((new Date()) + ": Server starts listening on port 8000");
});

//Listens on 'clientError' event and shutdown the socket gracefully 
httpServer.on('clientError', (err, socket) => {
    socket.end('HTTP/1.1 400 Bad Request\r\n\r\n');
});


/*****----------WebSocket reloated starts from here----------*****/ 
//https://github.com/theturtle32/WebSocket-Node/tree/cce6d468986dd356a52af5630fd8ed5726ba5b7a/docs
//WS Server ----> WS Request ----> WS Connection

//Create a Websocket Server 
console.log((new Date()) + ": Starting WebSocket server...");
const wsServerConfigOptions = {
    httpServer: httpServer,         //specify the HTTP server this WS server needs to be attached to
    autoAcceptConnections: false,   //if true, WS connection will be accepted regardless of the path and protocol specified by client 
    keepalive: true,
    keepaliveInterval: 10000,
    disableNagleAlgorithm: false    //Nagle Algorithm introduces a small delay before sending small packets so that multiple messages can be batched together, which introduces more latency.
}
const wsServer = new WebSocketServer(wsServerConfigOptions); 
console.log((new Date()) + ": WebSocket server created!");

//WebSocket Server listens on 'request' event and create a WsRequest handler 
wsServer.on('request', (wsReq) => {
    
    //Inspect the request object to make sure it's accpetable, i.e. protocol, user's origion, etc...
    if (!originIsAllowed(wsReq.origin)) {
        wsReq.reject(403, "Your WebSocket request is rejected due to Origin mismatch.");
        console.log((new Date()) + ": Connection from " + req.origin + " rejected.");
        return;
    }

    //Accept the WS request and create WS connection object
    var wsConnection = wsReq.accept(null,wsReq.origin)
    console.log((new Date()) + " Connection accepted. Connected with remote peer " + wsConnection.socket.remoteAddress + ' ' + wsReq.remoteAddress);
    connectionArray.push(wsConnection);

    //Send the new client its token; It will respond with its login username. 
    wsConnection.clientID = nextID;
    nextID++;
    var msg = {
        type: "id",
        id: wsConnection.clientID
    }
    wsConnection.sendUTF(JSON.stringify(msg));

    //WebSocket Connection listens on 'message' event and create a WsMessage handler
    wsConnection.on('message', (message) => {
        console.log((new Date()) + ": Message received from ", wsConnection.socket.remoteAddress)
        if (message.type === 'utf8'){
            console.log((new Date()) + ": " + message.utf8Data);

            var msg = JSON.parse(message.utf8Data);

            switch(msg.type) {
                case "username":
                    var res = {
                        type: "username",
                        data: msg.data
                    }
                    wsConnection.userName = msg.data;
                    wsConnection.sendUTF(JSON.stringify(res));
                    break;

                case "chat-text":
                    console.log(msg);
                    var res = {
                        type: "chat-received",
                        userName: wsConnection.userName,
                        data: msg.data
                    }
                    wsConnection.sendUTF(JSON.stringify(res));
                    break;
            }
        }
    })


    //store logged in user 

    //allow multiple connection 

    //distribute messages 

})


//check WS origin 
function originIsAllowed(origin) {
    return true; 
}