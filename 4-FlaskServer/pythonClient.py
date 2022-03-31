import socketio
import asyncio
import time
from aiortc import RTCPeerConnection, RTCSessionDescription,RTCIceCandidate,RTCConfiguration,RTCIceServer
import typing
import ctypes
import json

config = RTCConfiguration(
    iceServers=[
        RTCIceServer(
            urls = "stun:stun.l.google.com:19302"
            )
        ]
    )

peerConnections = {}

# asyncio
sio = socketio.AsyncClient()

@sio.event
async def connect():
    print('connected to server')
    await sio.emit("viewer")

@sio.event
def connect_error(data):
    print("The connection failed!")

@sio.event
async def disconnect():
    print('disconnected from server')

@sio.event
async def offer(broadcasterId,broadcasterDescription):
    print('offer from broadcasterId: ' + broadcasterId)

    peerConnection = RTCPeerConnection(config)
    peerConnections[broadcasterId] = peerConnection; 

    # if isinstance(broadcasterDescription,RTCSessionDescription):
    #     print("true")
    # else: 
    #     print("false")
    # print(broadcasterDescription)

    await peerConnection.setRemoteDescription(RTCSessionDescription(sdp=broadcasterDescription["sdp"], type=broadcasterDescription["type"]))
    
    # print (peerConnection.remoteDescription)

    answer = await peerConnection.createAnswer()

    # print (answer)

    await peerConnection.setLocalDescription(answer)

    print (peerConnection.localDescription)
    print (json.dumps({"type":answer.type, "sdp":answer.sdp}))

    await sio.emit("answer", (broadcasterId, vars(peerConnection.localDescription)))
    # await sio.emit("answer", (broadcasterId, json.dumps({"type":answer.type, "sdp":answer.sdp})))
    
    print ("answer sent")
    print (peerConnection.getReceivers())
    print (peerConnection.getSenders())
    print (peerConnection.getTransceivers())
    # print (id(peerConnection._RTCPeerConnection__iceTransports[]))


    @peerConnection.on('iceconnectionstatechange')
    def pc_on_iceconnectionstatechange():
        print("iceconnectionstatechange event")
        print(peerConnection.iceConnectionState)

    @peerConnection.on('connectionstatechange')
    def pc_on_connectionstatechange():
        print("connectionstatechange event")
        print(peerConnection.connectionState)

    @peerConnection.on('icecandidate')
    def pc_on_icecandidate():
        print("icecandidate")

    @peerConnection.on('track')
    def pc_on_track(): 
        print("track")


@sio.event
async def candidate(broadcasterId,candidate):
    
    candidateAttributes = candidate["candidate"].split()
    print("received candidate: ", candidateAttributes)

    if (len(candidateAttributes) > 6): 
        print("component type: ", type(int(candidateAttributes[1])))
        iceCandidate = RTCIceCandidate(
            component=int(candidateAttributes[1]), 
            foundation=candidateAttributes[0].split(":")[1], 
            ip=candidateAttributes[4], 
            port=int(candidateAttributes[5]), 
            priority=int(candidateAttributes[3]), 
            protocol=candidateAttributes[2],
            type=candidateAttributes[7],
            sdpMid=candidate["sdpMid"], 
            sdpMLineIndex=candidate["sdpMLineIndex"]
            )
        await peerConnections[broadcasterId].addIceCandidate(iceCandidate)
        print("candidate added")

async def start_connection():
    print("Trying to connect with server...")
    await sio.connect('http://localhost:4000')
    await sio.wait()

if __name__ == '__main__':
    asyncio.run(start_connection())