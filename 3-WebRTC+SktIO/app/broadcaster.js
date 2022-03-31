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
socket.on("viewer", (viewerId) => {
    console.log("viewer event, viewer ID received")
    const peerConnection = new RTCPeerConnection(config);
    peerConnections[viewerId] = peerConnection;  

    //add broadcaster video track to the peerConnection track 
    let stream = video.srcObject;
    stream.getTracks().forEach((track) => {
        peerConnection.addTrack(track,stream)
    })


    //create peerConnection offer
    peerConnection.createOffer()
    .then((sdp) => {
        peerConnection.setLocalDescription(sdp)
        .then(() => { 
            socket.emit("offer", viewerId, peerConnection.localDescription)
            console.log("sending offer")
        })

    })

    //handle the icecandidate event. This happens whenever the local ICE agent needs to deliver a message to the other peer through the signaling server. 
    peerConnection.onicecandidate = function(event) {
        if (event.candidate) {
            console.log("onicecandidate event")
            socket.emit("candidate", viewerId, event.candidate);  //???? viewer/candidate ID? 
        }
    }

    peerConnection.onicegatheringstatechange = event => {
        console.log(peerConnection.iceGatheringState)
    }

    peerConnection.onicegatheringstatechange = event => {
        console.log(peerConnection.iceGatheringState)
    }
    peerConnection.onconnectionstatechange = event => { console.log("onconnectionstatechange" + peerConnection.connectionState ) };
    peerConnection.iceconnectionstatechange   = event => { console.log("iceconnectionstatechange  " + peerConnection.iceConnectionSt  ) };

    socket.on("answer", (id,description) => {
        console.log("answer event: " + socket.id)  
        console.log("broadcasterId: " + id)
        console.log("viewerDescription: " + description)
        console.log('typeof viewerDescription: ', typeof description)
        peerConnections[id].setRemoteDescription(description)
        .catch(error => console.error(error))
        console.log(peerConnections[id])
    })
    

    socket.on("candidate", (id, candidate) => {
        console.log("candidate event: " + id + candidate)

        console.log(peerConnections[id])
        peerConnections[id].addIceCandidate(new RTCIceCandidate(candidate));
        console.log("new RTCIceCandidate(candidate)")
        console.log(peerConnections[id])
    })

})

socket.on("disconnectPeer", (id) => {
    peerConnections[id].close();
    delete peerConnections[id];
})

window.onunload = window.onbeforeunload = () => {
    socket.close();
  };