from app.models.game import Game
from app.db import SessionLocal
from app.db.models import GameDB
import json
from fastapi import HTTPException

class GameService:
    def __init__(self):
        self.games = {}  # room_id -> Game instance

    def create_game(self, room_id):
        if room_id in self.games:
            raise ValueError("Game already exists.")
        self.games[room_id] = Game(room_id)
        return self.games[room_id]

    def join_game(self, room_id, player_name):
        game = self.games.get(room_id)
        if not game:
            raise ValueError("Game not found.")
        game.add_player(player_name)

    def start_game(self, room_id):
        game = self.games.get(room_id)
        if not game:
            raise ValueError("Game not found.")
        game.start_game()

    def get_game(self, room_id):
        game = self.games.get(room_id)
        if not game:
            raise ValueError("Game not found.")
        return game

    def move_player(self, room_id, steps):
        game = self.get_game(room_id)
        return game.move_current_player(steps)

    def buy_property(self, room_id, property_id):
        game = self.get_game(room_id)
        return game.player_buy_property(property_id)

    def pay_rent(self, room_id, property_id):
        game = self.get_game(room_id)
        return game.player_pay_rent(property_id)

    def mortgage_property(self, room_id, property_id):
        game = self.get_game(room_id)
        return game.player_mortgage_property(property_id)

    def lift_mortgage(self, room_id, property_id):
        game = self.get_game(room_id)
        return game.player_lift_mortgage(property_id)

    def build_house(self, room_id, property_id):
        game = self.get_game(room_id)
        return game.player_build_house(property_id)

    def build_hotel(self, room_id, property_id):
        game = self.get_game(room_id)
        return game.player_build_hotel(property_id)

    def draw_chance_card(self, room_id):
        game = self.get_game(room_id)
        return game.player_draw_chance_card()

    def draw_community_chest_card(self, room_id):
        game = self.get_game(room_id)
        return game.player_draw_community_chest_card()

    def end_turn(self, room_id):
        game = self.get_game(room_id)
        return game.next_turn()

    def get_state(self, room_id):
        game = self.get_game(room_id)
        return game.get_state()

    def save_game(self, room_id):
        db = SessionLocal()
        game = self.games[room_id]
        state = game.get_state()
        game_db = db.query(GameDB).filter(GameDB.id == room_id).first()
        if not game_db:
            game_db = GameDB(id=room_id, state=state)
            db.add(game_db)
        else:
            game_db.state = state
        db.commit()
        db.close()

    def load_game(self, room_id):
        db = SessionLocal()
        game_db = db.query(GameDB).filter(GameDB.id == room_id).first()
        db.close()
        if game_db:
            # You need a method to restore a Game object from state
            game = Game(room_id)
            game.restore_state(game_db.state)
            self.games[room_id] = game
            return game
        else:
            raise ValueError("Game not found.")

game_service = GameService()