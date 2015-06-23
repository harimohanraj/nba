"""

Configuration

"""


from sqlalchemy.ext.declarative import declarative_base




# database configuration
database_settings = {
	'drivername': 'postgres',
	'host': 'localhost'
	'port': '5432',
	'username': 'YOUR_USERNAME',
	'password': 'YOUR_PASSWORD',
	'database': 'nbadb'
}

Base = declarative_base()