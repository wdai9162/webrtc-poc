let peerConnection; 

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

socket.on("offer", (broadcasterId, broadcasterDescription) => {
    peerConnection = new RTCPeerConnection(config);
    peerConnection
    .setRemoteDescription(broadcasterDescription)
    .then(() => peerConnection.createAnswer())
    .then(sdp => peerConnection.setLocalDescription(sdp))
    .then(() => {
      socket.emit("answer", broadcasterId, peerConnection.localDescription);
    });

    peerConnection.ontrack = event => {
        video.srcObject = event.streams[0];
      };

    peerConnection.onicecandidate = event => {
    if (event.candidate) {
        console.log("candidate event: " + event.candidate)
        socket.emit("candidate", broadcasterId, event.candidate);
    }
    };

})

socket.on("candidate", (id, candidate) => {
  console.log("received candidate on socket: " + candidate)
    peerConnection
      .addIceCandidate(new RTCIceCandidate(candidate))    //最后一步 adds this new remote candidate to the RTCPeerConnection's remote description, which describes the state of the remote end of the connection. 
      .catch(e => console.error(e));
  });
  
  socket.on("connect", () => {
    socket.emit("viewer", socket.id);
  });
  
  socket.on("broadcaster", () => {
    socket.emit("viewer");
  });
  
  window.onunload = window.onbeforeunload = () => {
    socket.close();
    peerConnection.close();
  };


  