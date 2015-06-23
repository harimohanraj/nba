"""
models.py
"""

from sqlalchemy import Column, Integer, String

# this should go in player.py ?
class Player(Base):
	__tablename__ = 'players'

	PERSON_ID = Column(Integer, primary_key=True)
	FIRST_NAME = Column(String)
	LAST_NAME = Column(String)
	HEIGHT = Column(String)
	WEIGHT = Column(String)
	SEASON_EXP = Column(Integer)
	POSITION = Column(String)
	ROSTERSTATUS = Column(String)
	TEAM_ID = Column(Integer)
	FROM_YEAR = Column(Integer)
	TO_YEAR = Column(Integer)

# this should go in a shotlog.py ?
class Shot(Base):
	__tablename__ = 'shots'

	playerID = Column(Integer)
	gameEventID = Column(Integer)
	gameID = Column(String)
	shot_x = Column(Numeric)
	shot_y = Column(Numeric)
	shot_type = Column(String)
