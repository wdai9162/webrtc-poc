//const { Socket } = require("socket.io");

const peerConnections = {};

//STUN server config ????
const config = {
    iceServers: [
        {
            urls: ["stun:stun.l.google.com:19302"]
        }
    ]
}

//Establish WS connection with window origin 
const socket = io.connect(window.location.origin);
const video = document.querySelector("video");

//Initialize Video stream 
//Media contrains
const constraints = {
    video: { facingMode: "user" }
    // Uncomment to enable audio
    // audio: true,
  };

navigator.mediaDevices
.getUserMedia(constraints)
.then(stream => {
video.srcObject = stream;
socket.emit("broadcaster");
})
.catch(error => console.error(error));

//Initialize RTCPeerConnection on viewer request
socket.on("viewer", (id) => {
    console.log("viewer event, viewer ID received")
    const peerConnection = new RTCPeerConnection(config);
    peerConnections[id] = peerConnection;  

    //add broadcaster video track to the peerConnection track 
    let stream = video.srcObject;
    stream.getTracks().forEach((track) => {
        peerConnection.addTrack(track,stream)
    })

    //handle the icecandidate event. This happens whenever the local ICE agent needs to deliver a message to the other peer through the signaling server. 
    peerConnection.onicecandidate = function(event) {
        if (event.candidate) {
            socket.emit("candidate", id, event.candidate);  //????
        }
    }

    //create peerConnection offer
    peerConnection.createOffer()
    .then((sdp) => {
        peerConnection.setLocalDescription(sdp)
        .then(() => {
            socket.emit("offer", id, peerConnection.localDescription)
        })
    })

    socket.on("answer", (id,description) => {
        peerConnections[id].setRemoteDescription(description);
    })

    socket.on("candidate", (id, candidate) => {
        peerConnections[id].addIceCandidate(new RTCIceCandidate(candidate));
    })

})

socket.on("disconnectPeer", (id) => {
    peerConnections[id].close();
    delete peerConnections[id];
})

window.onunload = window.onbeforeunload = () => {
    socket.close();
  };