from pydantic import BaseModel
from typing import List, Optional

class PlayerSchema(BaseModel):
    name: str
    money: int
    position: int

class GameStateSchema(BaseModel):
    room_id: str
    players: List[PlayerSchema]
    current_turn: Optional[str]
    started: bool

class CreateGameResponse(BaseModel):
    message: str

class JoinGameResponse(BaseModel):
    message: str

class StartGameResponse(BaseModel):
    message: str
