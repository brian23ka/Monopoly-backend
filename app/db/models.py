from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, JSON
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class GameDB(Base):
    __tablename__ = "games"
    id = Column(String, primary_key=True)
    state = Column(JSON)  # Store full game state as JSON

class PlayerDB(Base):
    __tablename__ = "players"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    game_id = Column(String, ForeignKey("games.id"))
    state = Column(JSON)  # Store player state as JSON