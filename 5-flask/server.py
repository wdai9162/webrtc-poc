from flask import Flask,render_template,request,jsonify
from aiortc import RTCPeerConnection, RTCSessionDescription,RTCIceCandidate,RTCIceServer
import uuid
import asyncio 
import socketio

app = Flask(__name__, 
            static_url_path='/static')

peerConnections = {}

# asyncio
sio = socketio.AsyncClient()

@app.route("/")
async def get_data():
    print("Get request '/'")
    return render_template('index.html')


@app.route('/offer', methods=['POST'])
async def offer():
    data = request.get_json()

    sdp = request.get_json()["sdp"]
    type = request.get_json()["type"]
    video_transform = request.get_json()["video_transform"]

    offer = RTCSessionDescription(sdp=sdp, type=type)

    pc = RTCPeerConnection()
    pc_id = "PeerConnection(%s)" % uuid.uuid4()
    peerConnections[pc_id]=(pc)



    # # # def log_info(msg, *args):
    # # #     logger.info(pc_id + " " + msg, *args)

    # # # log_info("Created for %s", request.remote)

    # # # prepare local media
    # # # player = MediaPlayer(os.path.join(ROOT, "demo-instruct.wav"))
    # # # if args.record_to:
    # # #     recorder = MediaRecorder(args.record_to)
    # # # else:
    # # #     recorder = MediaBlackhole()

    # @pc.on("datachannel")
    # def on_datachannel(channel):
    #     @channel.on("message")
    #     def on_message(message):
    #         if isinstance(message, str) and message.startswith("ping"):
    #             channel.send("pong" + message[4:])

    # @pc.on("connectionstatechange")
    # async def on_connectionstatechange():
    #     # log_info("Connection state is %s", pc.connectionState)
    #     if pc.connectionState == "failed":
    #         await pc.close()
    #         # pcs.discard(pc)

    # # @pc.on("track")
    # # def on_track(track):
    # #     # log_info("Track %s received", track.kind)

    # #     if track.kind == "audio":
    # #         pc.addTrack(player.audio)
    # #         recorder.addTrack(track)
    # #     elif track.kind == "video":
    # #         pc.addTrack(
    # #             VideoTransformTrack(
    # #                 relay.subscribe(track), transform=params["video_transform"]
    # #             )
    # #         )
    # #         if args.record_to:
    # #             recorder.addTrack(relay.subscribe(track))

    # #     @track.on("ended")
    # #     async def on_ended():
    # #         log_info("Track %s ended", track.kind)
    # #         await recorder.stop()

    # handle offer
    await pc.setRemoteDescription(offer)
    # await recorder.start()

    # send answer
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)
     
    data = {
            "content_type" : "application/json",
            "text" : {"sdp": pc.localDescription.sdp, "type": pc.localDescription.type},
        }
    
    response = jsonify(data)
    response.status_code = 200
    return response

    # return app.Response(
    #     content_type="application/json",
    #     text=json.dumps(
    #         {"sdp": pc.localDescription.sdp, "type": pc.localDescription.type}
    #     ),
    # )

async def start_connection():
    print("Trying to connect with server...")
    await sio.connect('http://localhost:4000')
    print("Server started")
    # await sio.wait()

async def main():

    # tasks = []
    # tasks.append(asyncio.create_task(start_connection()))
    # tasks.append(asyncio.create_task(app.run(debug=True)))
    # await asyncio.gather(*tasks)
    while True:
        await start_connection()
        app.run(debug=True)
        
        

if __name__ == '__main__':
    # asyncio.run(main())
    loop = asyncio.get_event_loop()
    loop.create_task(start_connection())
    loop.create_task(app.run(debug=True))
    loop.run_forever()
        
    
    