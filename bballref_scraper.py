"""
Simple web-scraper for college-level basketball data from www.basketball-reference.com.
Iterates through player list, checks for existence of page based on name and draft year,
and returns final-year college statistics if they exist. 
"""

import csv
import requests
import pandas as pd
from bs4 import BeautifulSoup
from pprint import pprint

missing = list()
share = list()
found = list()
player_list = pd.read_csv('nba_draft.csv')['name'].tolist()

for player in player_list:
	data = {'search': player}
	r = requests.get("http://www.sports-reference.com/cbb/search.cgi",params=data)
	if not r.history: 
		if r.text.encode('utf-8').find('0 hits') != -1:
			print(player+' not found / no college.')
			missing.append([player, 'NA'])
		else:
			print(player+' shares name.')
			share.append([player, 'SN'])
	else:
		soup = BeautifulSoup(r.text)
		year = [tag.text.encode('utf-8') for tag in soup.find(id='players_totals').find_all('tr')[-2].find_all('td')]
		year.insert(0,player)
		found.append(year)
		print(player+' found.')


with open('college_stats.csv','wb') as f:
	writer = csv.writer(f)
	writer.writerows(found)

with open('missing.csv','wb') as f:
	writer = csv.writer(f)
	writer.writerows(missing)

with open('share.csv','wb') as f:
	writer = csv.writer(f)
	writer.writerows(share)







