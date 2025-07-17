import os
from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import socketio
import uvicorn

load_dotenv()

# FastAPI app setup
app = FastAPI(title="CodeArena API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Socket.IO server setup
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')
socket_app = socketio.ASGIApp(sio, other_asgi_app=app)


@app.get("/")
async def read_root():
    return {"message": "Welcome to CodeArena Backend"}

# Socket.IO events
@sio.event
async def connect(sid, environ):
    print(f"connect {sid}")
    await sio.emit('message', {'data': f'Client {sid} connected'}, to=sid)

@sio.event
async def disconnect(sid):
    print(f"disconnect {sid}")

@sio.on('chat_message')
async def handle_chat_message(sid, data):
    print(f"Message from {sid}: {data}")
    await sio.emit('chat_message', {'sid': sid, 'message': data['message']})

if __name__ == "__main__":
    uvicorn.run("main:socket_app", host="0.0.0.0", port=8000, reload=True)

# Powered by Innovate CLI, a product of vaidik.co
