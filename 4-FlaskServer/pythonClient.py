import re
from flask import Flask, render_template,send_from_directory, request
from flask_socketio import SocketIO
import socketio
import asyncio
from aiortc import RTCPeerConnection, RTCSessionDescription,RTCIceCandidate,RTCConfiguration,RTCIceServer
from aiortc import MediaStreamTrack, RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaBlackhole, MediaPlayer, MediaRecorder, MediaRelay
import typing
import ctypes
import json
import time
import logging

# sio server config
app = Flask(__name__, 
            static_url_path='/static')

# WebRTC peerconnection config
config = RTCConfiguration(
    iceServers=[
        RTCIceServer(
            urls = "stun:stun.l.google.com:19302"
            )
        ]
    )

logger = logging.getLogger("pc")

# asyncio
sio = socketio.AsyncClient()

# a dict to hold all peer connections
peerConnections = {}


@app.route("/")
def index():
    print("Get request '/'")
    return render_template('index.html')

@app.route('/offer', methods=['POST'])
async def offer():
    
    sdp = await request.form["sdp"]
    type = await request.form["type"]

    print(sdp)
    video_transform = request.form["video_transform"]
    
    offer = RTCSessionDescription(sdp=params["sdp"], type=params["type"])
    
    pc = RTCPeerConnection()
    pc_id = "PeerConnection(%s)" % uuid.uuid4()
    peerConnections[pc_id]=(pc)



    # # def log_info(msg, *args):
    # #     logger.info(pc_id + " " + msg, *args)

    # # log_info("Created for %s", request.remote)

    # # prepare local media
    # # player = MediaPlayer(os.path.join(ROOT, "demo-instruct.wav"))
    # # if args.record_to:
    # #     recorder = MediaRecorder(args.record_to)
    # # else:
    # #     recorder = MediaBlackhole()

    @pc.on("datachannel")
    def on_datachannel(channel):
        @channel.on("message")
        def on_message(message):
            if isinstance(message, str) and message.startswith("ping"):
                channel.send("pong" + message[4:])

    @pc.on("connectionstatechange")
    async def on_connectionstatechange():
        # log_info("Connection state is %s", pc.connectionState)
        if pc.connectionState == "failed":
            await pc.close()
            # pcs.discard(pc)

    @pc.on("track")
    def on_track(track):
        log_info("Track %s received", track.kind)

    #     if track.kind == "audio":
    #         pc.addTrack(player.audio)
    #         recorder.addTrack(track)
    #     elif track.kind == "video":
    #         pc.addTrack(
    #             VideoTransformTrack(
    #                 relay.subscribe(track), transform=params["video_transform"]
    #             )
    #         )
    #         if args.record_to:
    #             recorder.addTrack(relay.subscribe(track))

    #     @track.on("ended")
    #     async def on_ended():
    #         log_info("Track %s ended", track.kind)
    #         await recorder.stop()

    # handle offer
    await pc.setRemoteDescription(offer)
    # await recorder.start()

    # send answer
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    return app.Response(
        content_type="application/json",
        text=json.dumps(
            {"sdp": pc.localDescription.sdp, "type": pc.localDescription.type}
        ),
    )


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

    def log_info(msg, *args):
        logger.info(pc_id + " " + msg, *args)

    peerConnection = RTCPeerConnection(config)
    peerConnections[broadcasterId] = peerConnection; 

    # if isinstance(broadcasterDescription,RTCSessionDescription):
    #     print("true")
    # else: 
    #     print("false")
    # print(broadcasterDescription)

    await peerConnection.setRemoteDescription(RTCSessionDescription(sdp=broadcasterDescription["sdp"], type=broadcasterDescription["type"]))
    answer = await peerConnection.createAnswer()


    await peerConnection.setLocalDescription(answer)

    # print (peerConnection.localDescription)
    # print (json.dumps({"type":answer.type, "sdp":answer.sdp}))

    await sio.emit("answer", (broadcasterId, vars(peerConnection.localDescription)))
    
    print ("answer sent")
    print (peerConnection.getReceivers())
    print (peerConnection.getSenders())
    print (peerConnection.getTransceivers())
    # print (id(peerConnection._RTCPeerConnection__iceTransports[]))


    @peerConnection.on('iceconnectionstatechange')
    def pc_on_iceconnectionstatechange():
        print("iceconnectionstatechange event")
        print(peerConnection.iceConnectionState)

    # @peerConnection.on('connectionstatechange')
    # def pc_on_connectionstatechange():
    #     print("connectionstatechange event")
    #     print(peerConnection.connectionState)

    @peerConnection.on('icecandidate')
    def pc_on_icecandidate():
        print("icecandidate")

    # @peerConnection.on('track')
    # def pc_on_track(track): 
    #     print("track")

    @peerConnection.on("connectionstatechange")
    async def on_connectionstatechange():
        log_info("Connection state is %s", peerConnection.connectionState)
        if peerConnection.connectionState == "failed":
            await peerConnection.close()
            peerConnections.pop(broadcasterId)

    @peerConnection.on("track")
    def on_track(track):
        log_info("Track %s received", track.kind)
        print("PRINTTTTTTTT Track %s received", track.kind)

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
    await sio.connect('http://localhost:8080')
    print("server started")
    # await sio.wait()


async def main():
    await start_connection()
    

if __name__ == '__main__':
    asyncio.run(main())
    
    
    