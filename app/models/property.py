# app/models/property.py
from app.utilis.helpers import PROPERTY_NAMES, PROPERTY_PRICES, PROPERTY_RENTS_DETAILED, COLOUR_SETS, get_property_rent

class Property:
    def __init__(self, property_id):
        self.id = property_id
        self.name = PROPERTY_NAMES.get(property_id, "")
        self.price = PROPERTY_PRICES.get(property_id, 0)
        self.owner = None
        self.houses = 0
        self.hotel = False
        self.mortgaged = False

    def buy(self, player):
        if self.owner is None and player.money >= self.price:
            player.money -= self.price
            self.owner = player
            player.properties.append(self.id)
            return True
        return False

    def build_house(self):
        if self.hotel or self.houses >= 4:
            return False
        self.houses += 1
        return True

    def build_hotel(self):
        if self.houses == 4 and not self.hotel:
            self.hotel = True
            self.houses = 0
            return True
        return False

    def mortgage(self):
        if not self.mortgaged:
            self.mortgaged = True
            return self.price // 2
        return 0

    def lift_mortgage(self):
        if self.mortgaged:
            self.mortgaged = False
            return int(self.price * 0.55)
        return 0

    def get_rent(self, color_set_owned=False, railroads_owned=1, utilities_owned=1, dice_roll=0):
        return get_property_rent(
            self.id,
            houses=self.houses,
            hotel=self.hotel,
            color_set_owned=color_set_owned,
            railroads_owned=railroads_owned,
            utilities_owned=utilities_owned,
            dice_roll=dice_roll
        )
