"""
utilities for NBAPI
"""

######################
# Pipeline utilities #
######################

def apiRequest(api, parameters):
	"""
	Simple wrapper function for API requests. Use for a single API call.

	@param api: URL specifying target API.
	@param parameters: dictionary of parameters.
	"""
	resp = requests.get(api, params=parameters)
	try:
		resp.raise_for_status()
	except requests.exceptions.HTTPError:
		print("something got fucked up.")
	return resp.json()

def apiRequests(api, parameters, workers=3):
	"""
	Simple wrapper generator for API requests. Use for many async API calls.

	@param api: URL specifying target API.
	@param parameters: iterable of parameters in dictionary format.
	@param workers: number of processes working on requests
	"""
	with concurrent.futures.ProcessPoolExecutor(max_workers=workers) as executor:
		futures = executor.map(apiRequest, parameters)
		for future in concurrent.futures.as_completed(futures):
			yield future.result().json()

def stripJSON(json):
	"""
	Necessary for stats.nba.com's API response format.
	"""
	return json['resultSets'][0]

def itemGenerator(json, keys, data):
	"""
	Generator that generates an item from the given JSON from stats.nba.com. This item is 
	a dictionary where the keys are the variable and the data are the associated value. 
	Basically, this is flattening JSON into a lazy factory that yields entries into an RDBMS.

	@param json: json object returned from API request.
	@param keys: json attribute that identifies headers.
	@param data: json attribute that identifies data belonging to headers.
	"""
	keys = json[keys]
	items = [dict(zip(keys, row)) for row in json[data]]
	for item in items:
		yield item

def itemMapper(items, func):
	"""
	Generator that maps a function to the given item. This can be used to transform /
	process raw API data. It yields the new item with the given function applied.

	@param items: generator of items yielded by itemGenerator.
	@param func: function that transforms item. Must return a valid item (dictionary).
	"""
	for item in items:
		item = func(item)
		yield item

def itemFilter(items, func):
	"""
	Generator that filters a given item on an attribute in the item. This can
	be used as part of a data processing pipeline to limit what we store from the API.

	@param items: generator of items yielded by itemGenerator.
	@param func: function that filters item. Must return a boolean. 
	"""
	for item in items:
		if func(item):
			yield item

######################
# database utilities #
######################

def connectToDB(settings, logging = False):
	"""
	Connect to database using supplied settings. Returns a SQLAlchemy 
	engine instance.

	@param _settings: dictionary of database settings from config.py.
	@param _logging: logging option for SQLAlchemy engine.
	"""
	return create_engine(**settings, logging)

def initializeTables(engine, base):
	"""
	Initializes database tables.

	@param base: declarative Base instance that registers tables. 
	@param engine: SQLAlchemy engine instance.
	"""
	base.metadata.create_all(engine)


def writeToTable(data, tablename, conn):
	"""
	Takes an iterable of dictionary items and inserts it into a database.

	@param data: iterable of dictionary items to be inserted into db.
	@param table_name: name of table that data is written to.
	@param conn: database connection object.
	"""





