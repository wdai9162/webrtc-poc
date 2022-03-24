from flask import Flask, render_template
from flask_socketio import SocketIO
import socketio

# standard Python
sio = socketio.Client()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'

socketio = SocketIO(app) 

@app.route("/")
def index():
    print("Get request '/'")
    return render_template('index.html')

@socketio.on('viewer')
def handle_viewer_event(arg1):
    print('received args: ' + arg1["data"])
    sio.connect('http://localhost:4000')
    print('proxy server sid is', sio.sid)
    #@sio.on(connect)
    sio.emit('viewer', {'foo': 'bar'})

if __name__ == '__main__':
    socketio.run(app)