from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from app.services.websocket_manager import WebSocketManager
from fastapi.middleware.cors import CORSMiddleware
from app.routes import game_routes


app = FastAPI()
manager = WebSocketManager()

# Allow your frontend (React) to connect to this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # later restrict this to your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Monopoly backend is running!"}

# WebSocket endpoint — handles real-time communication
@app.websocket("/ws/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str):
    await manager.connect(websocket, room_id)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(room_id, data)
    except WebSocketDisconnect:
        manager.disconnect(websocket, room_id)
        await manager.broadcast(room_id, "A player has left the game.")


app.include_router(game_routes.router, prefix="/game", tags=["game"])
