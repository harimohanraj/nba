
"""

# To Do 
~ allow for selection of single season, range of seasons, etc.
~ allow for specification of output file name, location
~ allow for smart rebuilding (i.e. if you have data, don't rebuild)

~ hit API for player info and merge into table
~ rip out table logic & generalize, for scraping all APIs
~ specify in-memory database feature, for interactivity
~ how to reduce # of API calls ? should we sleep & hit multiple at once?


game level shot logs
http://stats.nba.com/stats/shotchartdetail?CFID=&CFPARAMS=&ContextFilter=&ContextMeasure=FGA&DateFrom=&DateTo=&EndPeriod=10&EndRange=28800&GameID=&GameSegment=&LastNGames=0&LeagueID=00&Location=&Month=0&OpponentTeamID=0&Outcome=&Period=0&PlayerID=201956&Position=&RangeType=2&RookieYear=&Season=2014-15&SeasonSegment=&SeasonType=Regular+Season&StartPeriod=1&StartRange=0&TeamID=1610612758&VsConference=&VsDivision=

"""

import os, sys, datetime
import requests, argparse
import json, gzip, sqlite3
import concurrent.futures
from requests_futures.sessions import FuturesSession
import traceback # debugging file permissions :(

# config
_leagueID = '00'
_rosterBaseURL = "http://stats.nba.com/stats/commonallplayers"
_playerInfoURL = "http://stats.nba.com/stats/commonplayerinfo"

# main
def run():

	#################
	# Option parser #
	#################

	# command line arguments
	parser = argparse.ArgumentParser(description="NBA League Roster Builder")
	parser.add_argument('--season', type=str, default='current', choices=['current','all'], help="defines what on timeline to build league roster")
	parser.add_argument('--storage', type=str, default='json', choices=['json', 'sql'], help='defines how roster data is stored on disk')
	args = parser.parse_args()

	# calculate season
	now = datetime.datetime.now().date()
	currentYear = now.year 
	seasonStart = datetime.date(currentYear, 10, 30)
	yearSplit = datetime.date(currentYear, 12, 31)
	if seasonStart <= now <= yearSplit:
		season = str(currentYear)+"-"+str(currentYear+1)[-2:]
	else: 
		season = str(currentYear-1)+"-"+str(currentYear)[-2:]

	# determine if roster is historical or current season only
	thisSeason = 1 if args.season == 'current' else 0

	# check if database directory exists, try to build, exit on failure
	try:
		os.makedirs("database", exist_ok=True)
	except OSError as e:
		print("I don't have permission to create the database directory. I'm going to exit now.")
		# traceback.print_exc(file=sys.stdout)
		sys.exit(1)


	############
	# Scraping #
	############

	# build league roster from initial api
	payload = {'IsOnlyCurrentSeason': thisSeason, 'LeagueID': _leagueID, 'Season': season}
	rosterResponse = requests.get(_rosterBaseURL, params=payload)
	try:
		rosterResponse.raise_for_status()
	except requests.exceptions.HTTPError as e:
		print("I can't connect to the API, error %s" % e.rosterResponse.status_code)
		print("Try running me again. Goodbye.")
		sys.exit(1)
	rosterJSON = rosterResponse.json()['resultSets'][0]

	# build player profiles from league roster
	# profile request processing pipeline
	def rosterGenerator():
		"""
		Generator that yields individual player JSON object.
		"""
		keys = rosterJSON['headers']
		roster = [dict(zip(keys, row)) for row in rosterJSON['rowSet']]
		for player in roster:
			yield player

	def jsonFilter(players, params, attribute, attrName):
		"""
		Filter that yields single attribute of player JSON.
		"""
		for player in players:
			parameter = params
			parameter[str(attrName)] = str(player[str(attribute)])
			yield parameter

	def requestPool(parameters, url):
		"""
		Generator that asynchronously processes profile requests and yields profile futures.
		"""
		session = FuturesSession(max_workers=10)
		for parameter in parameters:
			future = session.get(url, params=parameter)
			yield future

	def playerProfiles(futures):
		"""
		Generator that collects player profile futures
		"""
		for future in futures:
			yield future.result()

	_defaultPayload = {'LeagueID':_leagueID, 'SeasonType':'Regular Season'}
	roster = rosterGenerator()
	playerIDs = jsonFilter(roster, params=_defaultPayload, attribute='PERSON_ID', attrName='PLAYERID')
	playerFutures = requestPool(playerIDs, _playerInfoURL)
	players = playerProfiles(playerFutures)

	for player in players:
		print(player.url)
		print(player.status_code)


	################
	# Data Storage #
	################

	if args.storage == "json":
		_jsonDataPath = os.path.join(os.path.sep, os.getcwd(), 'database', 'players.json')
		try:
			with open(_jsonDataPath, 'w') as f:
				json.dump(rosterJSON, f, indent=4, sort_keys=True)
		except OSError:
			print(os.getcwd())
			print('I do not have write access to "%s".' % _jsonDataPath)
			print("I can't update the database. I'm going to exit now.")
			traceback.print_exc(file=sys.stdout)
			sys.exit(1)
	if args.storage == "sql":
		_sqlDataPath = os.path.join(os.path.sep, os.getcwd(), 'database', 'players.db')
		try:
			roster = rosterJSON['rowSet']
			db = sqlite3.connect(_sqlDataPath)
			db.execute('create table roster ' + '(playerID integer, name text, rosterStatus integer, fromYear integer, toYear integer, playerCode text)')
			for row in roster:
				db.execute('insert into roster values (?, ?, ?, ?, ?, ?)', row)
		except Error as e:
			print("Error: '%s'", e)
			print('I do not have write access to "%s".' % _sqlDataPath)
			print("I can't update the database. I'm going to exit now.")
			traceback.print_exc(file=sys.stdout)
			sys.exit(1)

# execute
if __name__ == '__main__':
	run()




