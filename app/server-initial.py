from flask import Flask, jsonify, request
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app)

# REST API to upload data
@app.route('/upload', methods=['POST'])
def upload_data():
    data = request.json
    print(f"Data received: {data}")
    return jsonify({"status": "success", "received": data})

# WebSocket event to handle interrupts
@socketio.on('interrupt')
def handle_interrupt(message):
    print(f"Interrupt received: {message}")
    emit('response', {'status': 'interrupt acknowledged'})

# Serve frontend
@app.route('/')
def index():
    return "Hello! This is your web app."

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)

