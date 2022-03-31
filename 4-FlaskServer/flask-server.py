from flask import Flask, render_template
from flask_socketio import SocketIO
import socketio
import asyncio
from aiortc import RTCPeerConnection, RTCSessionDescription,RTCIceCandidate,RTCIceServer

# sio client 
sioClient = socketio.Client()

# sio server 
async_mode = None
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
sioServer = SocketIO(app, async_mode=async_mode)

peerConnections = {}
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

@app.route("/")
def index():
    print("Get request '/'")
    return render_template('index.html')

@sioClient.on('connect')
def sio_connect():
    sioClient.emit('viewer', {'foo': 'bar'})
    print('proxy is connected to server, SID = ', sioClient.sid)

@sioClient.on('candidate')
def sio_candidate(broadcasterId,candidate):
    print("candidate event: ")
    print(candidate)
    if (len(candidate["candidate"].split()) > 6): 
        iceCandidate = RTCIceCandidate(
            component=candidate["candidate"].split()[1], 
            foundation=candidate["candidate"].split()[0].split(":")[1], 
            ip=candidate["candidate"].split()[4], 
            port=candidate["candidate"].split()[5], 
            priority=candidate["candidate"].split()[3], 
            protocol=candidate["candidate"].split()[2],
            type=candidate["candidate"].split()[6],
            sdpMid=candidate["sdpMid"], 
            sdpMLineIndex=candidate["sdpMLineIndex"]
            )
        print("icecandidate = ", iceCandidate)
        try: 
            loop.run_until_complete(peerConnections[broadcasterId].addIceCandidate(iceCandidate))
            print("addIceCandidate successful")
            print(peerConnections[broadcasterId].iceConnectionState)
        except: 
            print("An exception occurred")


@sioClient.on('offer')
def sio_offer(broadcasterId,broadcasterDescription): 
    print("offer event")
    # print(broadcasterDescription)
    peerConnection = RTCPeerConnection()
    peerConnections[broadcasterId] = peerConnection;  

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    offer = RTCSessionDescription(sdp=broadcasterDescription["sdp"], type=broadcasterDescription["type"])
    # print(offer)

    # @peerConnection.on('icecandidate')
    # def sio_on_offer(candidate):
    #     print("candidate event: add ICE candidate and start")
    #     print(candidate)

    @peerConnection.on('iceconnectionstatechange')
    def pc_on_iceconnectionstatechange():
        print("iceconnectionstatechange event")
        print(peerConnection.iceConnectionState)

    @peerConnection.on('connectionstatechange')
    def pc_on_connectionstatechange():
        print("connectionstatechange event")
        print(peerConnection.connectionState)


    loop.run_until_complete(peerConnection.setRemoteDescription(offer))
    # print("remoteDescription is ", peerConnection.remoteDescription)
    answer = loop.run_until_complete(peerConnection.createAnswer())
    # print(answer)
    loop.run_until_complete(peerConnection.setLocalDescription(answer))
    # print(peerConnection.localDescription)
    # print(vars(peerConnection.localDescription))

    # print(peerConnection[0])
    sioClient.emit('answer', (broadcasterId, vars(peerConnection.localDescription)))

    


@sioServer.on('viewer')
def handle_viewer_event(arg1):
    print('received args: ' + arg1["data"])
    sioClient.connect('http://localhost:4000')
    print('proxy sid is', sioClient.sid)
 

    # @sio.event
    # def connect_error(data):
    #     print("The connection failed!")

# @sioClient.on('offer')
# async def sio_on_offer(broadcasterId,broadcasterDescription): 
#     print("offer event")
#     peerConnection = RTCPeerConnection()
#     peerConnection.setRemoteDescription(broadcasterDescription)
#     print(peerConnection.remoteDescription)

    # await peerConnection.setLocalDescription(await peerConnection.createAnswer())
    # await sioClient.emit('answer', broadcasterId, peerConnection.localDescription)

        # @peerConnection.on('candidate')
        # async def sio_on_offer(candidate):
        #     print("add ICE candidate and start")
        #     print(candidate)
        #     await peerConnection.addRemoteCandidate()

        # @peerConnection.on('iceconnectionstatechange')
        # def pc_on_iceconnectionstatechange():
        #     print(peerConnection.iceConnectionState)

        # @peerConnection.on('connectionstatechange')
        # def pc_on_connectionstatechange():
        #     print(peerConnection.connectionState)

if __name__ == '__main__':
    sioServer.run(app)
