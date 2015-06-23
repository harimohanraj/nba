"""
~ roster and player shot logs

@ at some point, need to import the relevant models, I'm guessing. that lets us register
the models with our Base object, which enables us to create the SQL engine connection and
create skeletons of our tables.

"""


# set config options 
from . import config
from . import player

roster_api = "http://stats.nba.com/stats/commonallplayers"
player_api = "http://stats.nba.com/stats/commonplayerinfo"

# utility functions
def playerFilter(item):
	keys_to_filter = ("PERSON_ID", "FIRST_NAME", "LAST_NAME", "HEIGHT", "WEIGHT", "SEASON_EXP", \
					  "POSITION", "ROSTERSTATUS", "TEAM_ID", "FROM_YEAR", "TO_YEAR")
	return {k: v for k, v in item.items() if k.startswith(keys_to_filter)}

# build scraping pipeline
roster_json = stripJSON(apiRequest(_api=roster_api, _parameters=roster_params))
roster = itemGenerator(_json=roster_json, _keys='headers', _data='rowSet')
roster = itemMapper(_items=roster, _func=lambda item: {'PLAYERID': item['PERSON_ID']})
players_json = apiRequests(_api=player_api, _parameters=roster)
players = itemGenerator(_json=players_json, _keys='headers', _data='rowSet')
players = itemMapper(_items=players, _func=stripJSON) # is this how to do that?
players = itemMapper(_items=players, _func=playerFilter)

# do database magic
engine = openDbConnection(_database)
config.Base.metadata.create_all(engine)
session = Session(bind=engine)
for player in players:
	try: 
		p = Player()
		session.commit()
	except:
		# voodoo magic
		session.rollback()
session.close()


#########################################

from . import utils
from . import config
from sqlalchemy.orm import sessionmaker


class Pipeline():
	""" Pipeline model. """

	def __init__(self):
		# variables


		# database management
		engine = connectToDB(config.database_settings)
		initializeTables(engine, config.Base)
		self.Session = sessionmaker(bind=engine)


class PlayerPipeline(Pipeline):
	""" Pipeline for building player database and shot logs. """

	def __init__(self):
		# variables

		# database management
		engine = connectToDB(config.database_settings)
		initializeTables(engine, config.Base)
		self.Session = sessionmaker(bind=engine)

	def process(self):

	def writeToPlayerTable(self):

