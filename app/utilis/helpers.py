import random

# 🎲 Roll two dice and return their values and total
def roll_dice():
    dice_1 = random.randint(1, 6)
    dice_2 = random.randint(1, 6)
    total = dice_1 + dice_2
    return {
        "dice_1": dice_1,
        "dice_2": dice_2,
        "total": total
    }

# Property positions and names (classic US Monopoly)
PROPERTY_NAMES = {
    1: "Mediterranean Avenue", 3: "Baltic Avenue", 5: "Reading Railroad", 6: "Oriental Avenue", 8: "Vermont Avenue", 9: "Connecticut Avenue",
    11: "St. Charles Place", 12: "Electric Company", 13: "States Avenue", 14: "Virginia Avenue", 15: "Pennsylvania Railroad",
    16: "St. James Place", 18: "Tennessee Avenue", 19: "New York Avenue", 21: "Kentucky Avenue", 23: "Indiana Avenue", 24: "Illinois Avenue",
    25: "B&O Railroad", 26: "Atlantic Avenue", 27: "Ventnor Avenue", 28: "Water Works", 29: "Marvin Gardens",
    31: "Pacific Avenue", 32: "North Carolina Avenue", 34: "Pennsylvania Avenue", 35: "Short Line", 37: "Park Place", 39: "Boardwalk"
}

# 🏠 Property prices
PROPERTY_PRICES = {
    1: 60, 3: 60, 5: 200, 6: 100, 8: 100, 9: 120, 11: 140, 12: 150, 13: 140, 14: 160,
    15: 200, 16: 180, 18: 180, 19: 200, 21: 220, 23: 220, 24: 240, 25: 200, 26: 260,
    27: 260, 28: 150, 29: 280, 31: 300, 32: 300, 34: 320, 35: 200, 37: 350, 39: 400
}

# Colour sets for quick lookup
COLOUR_SETS = {
    "brown": [1, 3],
    "light_blue": [6, 8, 9],
    "pink": [11, 13, 14],
    "orange": [16, 18, 19],
    "red": [21, 23, 24],
    "yellow": [26, 27, 29],
    "green": [31, 32, 34],
    "dark_blue": [37, 39],
}

# 💸 Rent values for sample properties (expand as needed)
PROPERTY_RENTS_DETAILED = {
    1:  [2, 10, 30, 90, 160, 250],   # Mediterranean Avenue
    3:  [4, 20, 60, 180, 320, 450],  # Baltic Avenue
    6:  [6, 30, 90, 270, 400, 550],  # Oriental Avenue
    8:  [6, 30, 90, 270, 400, 550],  # Vermont Avenue
    9:  [8, 40, 100, 300, 450, 600], # Connecticut Avenue
    11: [10, 50, 150, 450, 625, 750],# St. Charles Place
    13: [10, 50, 150, 450, 625, 750],# States Avenue
    14: [12, 60, 180, 500, 700, 900],# Virginia Avenue
    16: [14, 70, 200, 550, 750, 950],# St. James Place
    18: [14, 70, 200, 550, 750, 950],# Tennessee Avenue
    19: [16, 80, 220, 600, 800, 1000],# New York Avenue
    21: [18, 90, 250, 700, 875, 1050],# Kentucky Avenue
    23: [18, 90, 250, 700, 875, 1050],# Indiana Avenue
    24: [20, 100, 300, 750, 925, 1100],# Illinois Avenue
    26: [22, 110, 330, 800, 975, 1150],# Atlantic Avenue
    27: [22, 110, 330, 800, 975, 1150],# Ventnor Avenue
    29: [24, 120, 360, 850, 1025, 1200],# Marvin Gardens
    31: [26, 130, 390, 900, 1100, 1275],# Pacific Avenue
    32: [26, 130, 390, 900, 1100, 1275],# North Carolina Avenue
    34: [28, 150, 450, 1000, 1200, 1400],# Pennsylvania Avenue
    37: [35, 175, 500, 1100, 1300, 1500],# Park Place
    39: [50, 200, 600, 1400, 1700, 2000],# Boardwalk
}

RAILROAD_RENT = [25, 50, 100, 200]  # 1, 2, 3, 4 railroads owned
UTILITY_RENT = [4, 10]  # 1 utility, 2 utilities (times dice roll)

def get_property_rent(property_id, houses=0, hotel=False, color_set_owned=False, railroads_owned=1, utilities_owned=1, dice_roll=0):
    # Railroads
    if property_id in [5, 15, 25, 35]:
        return RAILROAD_RENT[railroads_owned-1]
    # Utilities
    if property_id in [12, 28]:
        multiplier = UTILITY_RENT[utilities_owned-1]
        return multiplier * dice_roll if dice_roll else multiplier * 7  # Default dice roll if not provided
    # Standard properties
    rent_table = PROPERTY_RENTS_DETAILED.get(property_id)
    if not rent_table:
        return 0
    if hotel:
        return rent_table[5]
    if houses > 0:
        return rent_table[houses]
    # If color set owned and no houses/hotel, double base rent
    base_rent = rent_table[0]
    return base_rent * 2 if color_set_owned else base_rent

# 🃏 Sample chance/community chest effects
CHANCE_CARDS = [
    {"message": "Advance to Go (Collect $200)", "effect": "move", "steps": 0, "amount": 200},
    {"message": "Bank error in your favor – collect $200", "effect": "earn", "amount": 200},
    {"message": "Doctor’s fees – Pay $50", "effect": "pay", "amount": 50},
    {"message": "Go to Jail – Do not pass Go, do not collect $200", "effect": "move", "steps": 10, "jail": True},
    {"message": "Advance to Illinois Ave.", "effect": "move", "steps": 24},
    {"message": "Advance to St. Charles Place", "effect": "move", "steps": 11},
    {"message": "Pay poor tax of $15", "effect": "pay", "amount": 15},
    {"message": "Your building loan matures – collect $150", "effect": "earn", "amount": 150},
    {"message": "Advance to Boardwalk", "effect": "move", "steps": 39},
    {"message": "Go back 3 spaces", "effect": "move", "steps": -3},
    {"message": "Pay each player $50", "effect": "pay_each", "amount": 50},
    {"message": "Take a ride on the Reading Railroad – if you pass Go, collect $200", "effect": "move", "steps": 5},
    {"message": "Advance to the nearest Utility", "effect": "move_nearest_utility"},
    {"message": "Advance to the nearest Railroad", "effect": "move_nearest_railroad"},
]

COMMUNITY_CHEST_CARDS = [
    {"message": "Income tax refund – collect $20", "effect": "earn", "amount": 20},
    {"message": "Pay hospital fees of $100", "effect": "pay", "amount": 100},
    {"message": "You have won second prize in a beauty contest – collect $10", "effect": "earn", "amount": 10},
    {"message": "Life insurance matures – collect $100", "effect": "earn", "amount": 100},
    {"message": "Receive $25 consultancy fee", "effect": "earn", "amount": 25},
    {"message": "Pay school fees of $50", "effect": "pay", "amount": 50},
    {"message": "You inherit $100", "effect": "earn", "amount": 100},
    {"message": "From sale of stock you get $50", "effect": "earn", "amount": 50},
    {"message": "Go to Jail – Do not pass Go, do not collect $200", "effect": "move", "steps": 10, "jail": True},
    {"message": "Holiday fund matures – receive $100", "effect": "earn", "amount": 100},
    {"message": "Collect $50 from every player", "effect": "collect_from_all", "amount": 50},
    {"message": "It is your birthday – collect $10 from every player", "effect": "collect_from_all", "amount": 10},
    {"message": "Advance to Go (Collect $200)", "effect": "move", "steps": 0, "amount": 200},
]

def draw_chance_card():
    return random.choice(CHANCE_CARDS)

def draw_community_chest_card():
    return random.choice(COMMUNITY_CHEST_CARDS)

# Baltic Avenue, owns full set, 2 houses
rent = get_property_rent(3, houses=2, color_set_owned=True)
# Boardwalk, hotel
rent = get_property_rent(39, hotel=True)
# Reading Railroad, owns 3 railroads
rent = get_property_rent(5, railroads_owned=3)
# Electric Company, owns both utilities, dice roll 8
rent = get_property_rent(12, utilities_owned=2, dice_roll=8)
