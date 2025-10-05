from fastapi import APIRouter, HTTPException
from app.services.game_service import game_service
from app.services.websocket_manager import websocket_manager

router = APIRouter()

@router.post("/create/{room_id}")
def create_game(room_id: str):
    try:
        game_service.create_game(room_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"message": f"Game {room_id} created successfully."}

@router.post("/join/{room_id}/{player_name}")
def join_game(room_id: str, player_name: str):
    try:
        game_service.join_game(room_id, player_name)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"message": f"{player_name} joined game {room_id}."}

@router.post("/start/{room_id}")
def start_game(room_id: str):
    try:
        game_service.start_game(room_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"message": f"Game {room_id} started."}

@router.get("/state/{room_id}")
def get_game_state(room_id: str):
    try:
        state = game_service.get_state(room_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return state

@router.post("/move")
def move_player(room_id: str, steps: int):
    try:
        pos = game_service.move_player(room_id, steps)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"position": pos}

@router.post("/buy")
def buy_property(room_id: str, property_id: int):
    try:
        result = game_service.buy_property(room_id, property_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"success": result}

@router.post("/pay_rent")
def pay_rent(room_id: str, property_id: int):
    try:
        rent = game_service.pay_rent(room_id, property_id)
        if rent == "bankrupt":
            player = game_service.get_game(room_id).get_current_player().name
            notify(room_id, f"{player} went bankrupt!", type="bankruptcy")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"rent": rent}

@router.post("/mortgage")
def mortgage_property(room_id: str, property_id: int):
    try:
        value = game_service.mortgage_property(room_id, property_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"mortgage_value": value}

@router.post("/lift_mortgage")
def lift_mortgage(room_id: str, property_id: int):
    try:
        payment = game_service.lift_mortgage(room_id, property_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"payment": payment}

@router.post("/build_house")
def build_house(room_id: str, property_id: int):
    try:
        result = game_service.build_house(room_id, property_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"success": result}

@router.post("/build_hotel")
def build_hotel(room_id: str, property_id: int):
    try:
        result = game_service.build_hotel(room_id, property_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"success": result}

@router.post("/draw_chance")
def draw_chance_card(room_id: str):
    try:
        card = game_service.draw_chance_card(room_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"card": card}

@router.post("/draw_community_chest")
def draw_community_chest_card(room_id: str):
    try:
        card = game_service.draw_community_chest_card(room_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"card": card}

@router.post("/end_turn")
def end_turn(room_id: str):
    try:
        next_player = game_service.end_turn(room_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    broadcast_state(room_id)
    notify(room_id, f"It is now {next_player}'s turn.", type="turn")
    return {"next_player": next_player}

@router.post("/trade")
def trade(room_id: str, from_player: str, to_player: str, property_id: int, amount: int):
    game = game_service.get_game(room_id)
    from_p = game.get_player(from_player)
    to_p = game.get_player(to_player)
    prop = game.get_property(property_id)
    if prop.owner != from_p:
        raise HTTPException(status_code=400, detail="Property not owned by trading player.")
    prop.owner = to_p
    from_p.properties.remove(property_id)
    to_p.properties.append(property_id)
    to_p.pay(amount)
    from_p.earn(amount)
    return {"success": True}

@router.post("/trade/propose")
def propose_trade(room_id: str, from_player: str, to_player: str, offer: dict, request: dict):
    game = game_service.get_game(room_id)
    try:
        trade = game.propose_trade(from_player, to_player, offer, request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    broadcast_state(room_id)
    notify(room_id, f"{from_player} proposed a trade to {to_player}", type="trade", payload=trade)
    return {"trade": trade}

@router.post("/trade/counter")
def counter_trade(room_id: str, from_player: str, offer: dict, request: dict):
    game = game_service.get_game(room_id)
    try:
        trade = game.counter_trade(from_player, offer, request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    broadcast_state(room_id)
    return {"trade": trade}

@router.post("/trade/accept")
def accept_trade(room_id: str, player: str):
    game = game_service.get_game(room_id)
    try:
        result = game.accept_trade(player)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    broadcast_state(room_id)
    notify(room_id, f"{player} accepted the trade!", type="trade")
    return {"success": result}

@router.post("/trade/reject")
def reject_trade(room_id: str, player: str):
    game = game_service.get_game(room_id)
    try:
        result = game.reject_trade(player)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    broadcast_state(room_id)
    return {"success": result}

@router.post("/trade/cancel")
def cancel_trade(room_id: str, player: str):
    game = game_service.get_game(room_id)
    try:
        result = game.cancel_trade(player)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    broadcast_state(room_id)
    return {"success": result}

@router.get("/trade/pending/{room_id}")
def get_pending_trade(room_id: str):
    game = game_service.get_game(room_id)
    trade = game.get_pending_trade()
    return {"trade": trade}

@router.get("/trade/history/{room_id}")
def get_trade_history(room_id: str):
    game = game_service.get_game(room_id)
    history = game.get_trade_history()
    return {"history": history}

@router.post("/chat/send")
def send_chat(room_id: str, player: str, message: str):
    chat_payload = {
        "type": "chat",
        "player": player,
        "message": message
    }
    websocket_manager.broadcast(room_id, chat_payload)
    return {"success": True}

def broadcast_state(room_id):
    state = game_service.get_state(room_id)
    websocket_manager.broadcast(room_id, state)

def notify(room_id, message, type="info", payload=None):
    notification = {
        "type": type,
        "message": message,
        "payload": payload
    }
    websocket_manager.broadcast(room_id, notification)
