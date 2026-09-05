import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from app.services.websocket_manager import websocket_manager
from fastapi.middleware.cors import CORSMiddleware
from app.routes import game_routes
from app.services.game_service import game_service


app = FastAPI()
manager = websocket_manager

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
        await websocket.send_json({"type": "state", "state": game_service.get_state(room_id) if room_id in game_service.games else None})
        while True:
            payload = json.loads(await websocket.receive_text())
            action = payload.get("action")
            player_name = payload.get("player")
            if action == "create":
                if room_id not in game_service.games:
                    game_service.create_game(room_id)
            elif action == "join":
                if room_id not in game_service.games:
                    game_service.create_game(room_id)
                game = game_service.get_game(room_id)
                game_service.join_game(room_id, player_name)
                if len(game.players) >= 2 and not game.started:
                    game_service.start_game(room_id)
            elif action == "roll":
                game_service.get_game(room_id).roll_for_player(player_name)
            elif action == "buy":
                game_service.get_game(room_id).buy_current_property(player_name)
            elif action == "pass":
                game_service.get_game(room_id).pass_purchase(player_name)
            elif action == "end_turn":
                game_service.end_turn(room_id)
            else:
                raise ValueError("Unknown action")
            await manager.broadcast(room_id, {"type": "state", "state": game_service.get_state(room_id)})
    except (ValueError, json.JSONDecodeError) as error:
        await websocket.send_json({"type": "error", "message": str(error)})
    except WebSocketDisconnect:
        manager.disconnect(websocket, room_id)
        await manager.broadcast(room_id, {"type": "notice", "message": "A player has left the game."})


app.include_router(game_routes.router, prefix="/game", tags=["game"])
