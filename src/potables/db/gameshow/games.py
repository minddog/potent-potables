from sqlalchemy import Column, Integer, String
import base

class Game(base.Declarative, base.GameshowBase):
    __tablename__ = 'games'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    host = Column(String(255), nullable=False)
    players = Column(Integer, nullable=False)