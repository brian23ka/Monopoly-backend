import random
import time
from app.models.property import Property
from app.utilis.helpers import (
    roll_dice,
    COLOUR_SETS,
    draw_chance_card,
    draw_community_chest_card,
    PROPERTY_NAMES
)

class Player:
    def __init__(self, name: str):
        self.name = name
        self.position = 0
        self.money = 1500
        self.properties = []
        self.in_jail = False
        self.jail_turns = 0
        self.has_jail_card = False
        self.trade_history = []

    def move(self, steps: int):
        self.position = (self.position + steps) % 40

    def pay(self, amount: int):
        self.money -= amount

    def earn(self, amount: int):
        self.money += amount

    def owns_color_set(self, color):
        return all(pid in self.properties for pid in COLOUR_SETS[color])

class Game:
    def __init__(self, room_id: str):
        self.room_id = room_id
        self.players = []
        self.current_turn = 0
        self.started = False
        self.properties = {pid: Property(pid) for pid in PROPERTY_NAMES.keys()}
        self.chance_deck = []
        self.community_deck = []
        self.pending_trade = None
        self.trade_history = []

    def add_player(self, player_name: str):
        if any(p.name == player_name for p in self.players):
            raise ValueError("Player already exists")
        player = Player(player_name)
        self.players.append(player)

    def start_game(self):
        if len(self.players) < 2:
            raise ValueError("Need at least 2 players")
        self.started = True
        self.current_turn = 0

    def roll_dice(self):
        return roll_dice()

    def next_turn(self):
        self.current_turn = (self.current_turn + 1) % len(self.players)
        return self.players[self.current_turn].name

    def get_state(self):
        return {
            "room_id": self.room_id,
            "players": [
                {"name": p.name, "money": p.money, "position": p.position, "properties": p.properties}
                for p in self.players
            ],
            "current_turn": self.players[self.current_turn].name if self.players else None,
            "started": self.started
        }

    def move_current_player(self, steps: int):
        if not self.started:
            raise ValueError("Game not started")
        current_player = self.players[self.current_turn]
        current_player.move(steps)
        return current_player.position

    def get_current_player(self):
        if not self.started:
            raise ValueError("Game not started")
        return self.players[self.current_turn]

    def player_buy_property(self, property_id):
        current_player = self.get_current_player()
        prop = self.properties[property_id]
        return prop.buy(current_player)

    def player_pay_rent(self, property_id):
        current_player = self.get_current_player()
        prop = self.properties[property_id]
        owner = prop.owner
        if not owner or owner == current_player:
            return 0
        color_set_owned = False
        for color, ids in COLOUR_SETS.items():
            if property_id in ids:
                color_set_owned = owner.owns_color_set(color)
        rent = prop.get_rent(color_set_owned=color_set_owned)
        current_player.pay(rent)
        owner.earn(rent)
        # Bankruptcy check
        if current_player.money < 0:
            self.players.remove(current_player)
            # Transfer properties to owner or bank
            for pid in current_player.properties:
                self.properties[pid].owner = owner
            return "bankrupt"
        return rent

    def player_mortgage_property(self, property_id):
        prop = self.properties[property_id]
        return prop.mortgage()

    def player_lift_mortgage(self, property_id):
        prop = self.properties[property_id]
        return prop.lift_mortgage()

    def player_build_house(self, property_id):
        prop = self.properties[property_id]
        return prop.build_house()

    def player_build_hotel(self, property_id):
        prop = self.properties[property_id]
        return prop.build_hotel()

    def player_draw_chance_card(self):
        card = draw_chance_card()
        player = self.get_current_player()
        effect = card.get("effect")
        if effect == "move":
            if card.get("jail"):
                self.send_player_to_jail(player)
            else:
                player.move(card.get("steps", 0))
        elif effect == "earn":
            player.earn(card.get("amount", 0))
        elif effect == "pay":
            player.pay(card.get("amount", 0))
        # Add more effects as needed
        return card

    def player_draw_community_chest_card(self):
        card = draw_community_chest_card()
        player = self.get_current_player()
        effect = card.get("effect")
        if effect == "move":
            if card.get("jail"):
                self.send_player_to_jail(player)
            else:
                player.move(card.get("steps", 0))
        elif effect == "earn":
            player.earn(card.get("amount", 0))
        elif effect == "pay":
            player.pay(card.get("amount", 0))
        # Add more effects as needed
        return card

    # Add a method to get a property by id
    def get_property(self, property_id):
        return self.properties.get(property_id)

    # Add a method to get a player by name
    def get_player(self, name):
        for player in self.players:
            if player.name == name:
                return player
        return None

    # Add a method to check if the game is over (optional)
    def is_game_over(self):
        active_players = [p for p in self.players if p.money > 0]
        return len(active_players) <= 1

    # Add a method to eliminate bankrupt players (optional)
    def eliminate_bankrupt_players(self):
        self.players = [p for p in self.players if p.money > 0]

    def send_player_to_jail(self, player):
        player.position = 10  # Jail position
        player.in_jail = True
        player.jail_turns = 0

    def attempt_jail_escape(self, player, dice):
        if dice["dice_1"] == dice["dice_2"]:
            player.in_jail = False
            player.jail_turns = 0
            return True
        player.jail_turns += 1
        if player.jail_turns >= 3:
            player.pay(50)
            player.in_jail = False
            player.jail_turns = 0
            return True
        return False

    def validate_trade(self, from_player, to_player, offer, request):
        from_p = self.get_player(from_player)
        to_p = self.get_player(to_player)
        # Validate money
        if offer.get("money", 0) > from_p.money:
            raise ValueError("Sender does not have enough money.")
        if request.get("money", 0) > to_p.money:
            raise ValueError("Receiver does not have enough money.")
        # Validate properties
        for pid in offer.get("properties", []):
            if pid not in from_p.properties:
                raise ValueError("Sender does not own all offered properties.")
        for pid in request.get("properties", []):
            if pid not in to_p.properties:
                raise ValueError("Receiver does not own all requested properties.")
        # Validate jail card
        if offer.get("jail_card", False) and not from_p.has_jail_card:
            raise ValueError("Sender does not have a Get Out of Jail Free card.")
        if request.get("jail_card", False) and not to_p.has_jail_card:
            raise ValueError("Receiver does not have a Get Out of Jail Free card.")

    def propose_trade(self, from_player, to_player, offer, request):
        self.validate_trade(from_player, to_player, offer, request)
        self.pending_trade = {
            "from": from_player,
            "to": to_player,
            "offer": offer,
            "request": request,
            "status": "pending",
            "timestamp": time.time()
        }
        return self.pending_trade

    def counter_trade(self, from_player, offer, request):
        if not self.pending_trade or self.pending_trade["to"] != from_player:
            raise ValueError("No trade to counter or not your turn to counter.")
        self.validate_trade(from_player, self.pending_trade["from"], offer, request)
        self.pending_trade["from"], self.pending_trade["to"] = self.pending_trade["to"], self.pending_trade["from"]
        self.pending_trade["offer"] = offer
        self.pending_trade["request"] = request
        self.pending_trade["status"] = "countered"
        self.pending_trade["timestamp"] = time.time()
        return self.pending_trade

    def accept_trade(self, player):
        if not self.pending_trade or self.pending_trade["to"] != player:
            raise ValueError("No trade to accept or not your turn to accept.")
        from_p = self.get_player(self.pending_trade["from"])
        to_p = self.get_player(self.pending_trade["to"])
        offer = self.pending_trade["offer"]
        request = self.pending_trade["request"]
        # Transfer money
        to_p.money += offer.get("money", 0)
        from_p.money -= offer.get("money", 0)
        from_p.money += request.get("money", 0)
        to_p.money -= request.get("money", 0)
        # Transfer properties
        for pid in offer.get("properties", []):
            if pid in from_p.properties:
                from_p.properties.remove(pid)
                to_p.properties.append(pid)
                self.properties[pid].owner = to_p
        for pid in request.get("properties", []):
            if pid in to_p.properties:
                to_p.properties.remove(pid)
                from_p.properties.append(pid)
                self.properties[pid].owner = from_p
        # Transfer jail cards
        if offer.get("jail_card", False):
            from_p.has_jail_card = False
            to_p.has_jail_card = True
        if request.get("jail_card", False):
            to_p.has_jail_card = False
            from_p.has_jail_card = True
        self.pending_trade["status"] = "accepted"
        self.trade_history.append(self.pending_trade)
        from_p.trade_history.append(self.pending_trade)
        to_p.trade_history.append(self.pending_trade)
        self.pending_trade = None
        return True

    def reject_trade(self, player):
        if not self.pending_trade or self.pending_trade["to"] != player:
            raise ValueError("No trade to reject or not your turn to reject.")
        self.pending_trade["status"] = "rejected"
        self.trade_history.append(self.pending_trade)
        self.pending_trade = None
        return True

    def cancel_trade(self, player):
        if not self.pending_trade or self.pending_trade["from"] != player:
            raise ValueError("No trade to cancel or not your trade.")
        self.pending_trade["status"] = "cancelled"
        self.trade_history.append(self.pending_trade)
        self.pending_trade = None
        return True

    def check_trade_expiry(self, expiry_seconds=120):
        if self.pending_trade and time.time() - self.pending_trade["timestamp"] > expiry_seconds:
            self.pending_trade["status"] = "expired"
            self.trade_history.append(self.pending_trade)
            self.pending_trade = None

    def get_pending_trade(self):
        self.check_trade_expiry()
        return self.pending_trade

    def get_trade_history(self):
        return self.trade_history

    def restore_state(self, state):
        # Implement restoring all attributes from state dict
        self.room_id = state["room_id"]
        # Restore players, properties, etc.
