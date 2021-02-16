from selenium import webdriver
import pandas as pd 
from sqlalchemy import create_engine
from bs4 import BeautifulSoup as bs
import os

def login():
	from StatPuts import username, password
	login_address = 'https://stathead.com/users/login.cgi?token=1&redirect_uri=https%3A//www.basketball-reference.com/'
	browser = webdriver.Chrome(executable_path=r'chromedriver.exe')
	browser.get(login_address)
	user_name = browser.find_element_by_id('username')
	user_name.send_keys(username)
	pass_word = browser.find_element_by_id('password')
	pass_word.send_keys(password)
	browser.find_element_by_id('login').submit()
	return browser

def search():
	from StatPuts import s_year, ys, d_type
	start_year = int(s_year)
	years = int(ys)
	if d_type == "per36" or d_type =="pergame":
		d_type = "totals"
	return start_year,years,d_type

def scraper():
	browser = login()
	start_year,years,data_type = search()
	files_list = []
	player_ids = []
	for x in range(1, years+1):
		browser.get(f'https://www.basketball-reference.com/leagues/NBA_{start_year}_{data_type}.html')
		site_address = browser.current_url
		## The next several lines of code (until ['Season']) are to clean each base data type specifically 
		# do not bring year_df for 'shooting'...need to drop headers
		if data_type == 'shooting':
			year_df = shooting(site_address)
		else:
			year_df = pd.read_html(site_address)[0] # our data is the first table on the page
		if data_type == 'totals':
			year_df = totals(year_df)
		if data_type == 'play-by-play':
			year_df = play_by_play(year_df)
		if data_type == 'advanced':
			year_df = advanced(year_df)
		if data_type == 'per_poss':
			year_df = per_100(year_df)
		year_df['Season'] = start_year
		new_ids = player_id(browser)
		for each_id in new_ids:
			player_ids.append(each_id)
		year_df.to_csv(f'FlaskFiles/{start_year}{data_type}.csv') # after extracting, save to csv by year
		files_list.append(f'FlaskFiles/{start_year}{data_type}.csv') # append file name to files_list
		del year_df # delete the DataFrame from memory
		start_year += 1 # change the year to get next	
	browser.quit()
	df_from_each_file = (pd.read_csv(f) for f in files_list)
	all_df = pd.concat(df_from_each_file, ignore_index=True)
	all_df = cleaner(all_df, player_ids)
	for f in files_list:
		os.remove(f)
	return all_df

def player_id(browser):
	html = browser.page_source
	soup = bs(html, "html.parser")
	results = soup.find_all('td', class_='left')
	player_ids = []
	for result in results:
		try:
			if result.attrs['data-append-csv']:
				player_ids.append(result.attrs['data-append-csv'])
		except:
			pass
	return player_ids

def advanced(year_df):
	year_df = year_df.rename(columns={
		'TS%':'TS',
		'ORB%':'ORB',
		'DRB%':'DRB',
		'TRB%':'TRB',
		'AST%':'AST',
		'STL%':'STL',
		'BLK%':'BLK',
		'TOV%':'TOV',
		'USG%':'USG',
		'WS/48':'WS_48',
		'3PAr': "Ar3P"
		})
	return year_df

def totals(year_df):
	year_df = year_df.rename(columns={
		'FG%':'FGPc',
		'3P%':'_3PTPc',
		'2P%':'_2PTPc',
		'FT%':'FTPc',
		'3P':'_3P',
		'3PA':'_3PA',
		'2P':'_2P',
		'2PA':'_2PA',
		'eFG%':'eFGPc'
		})
	return year_df

def per_100(year_df):
	year_df = year_df.rename(columns={
		'FG%':'FGPc',
		'3P%':'_3PTPc',
		'2P%':'_2PTPc',
		'FT%':'FTPc',
		'3P':'_3P',
		'3PA':'_3PA',
		'2P':'_2P',
		'2PA':'_2PA',
		})
	return year_df


def play_by_play(year_df):
	year_df.columns = year_df.columns.droplevel()
	# Change columns with multiple names (Shoot, Off.)
	cols = []
	scount, ocount = 1, 1
	for column in year_df.columns:
	    if column == 'Shoot':
	        cols.append(f'Shoot_{scount}')
	        scount+=1
	        continue
	    elif column == 'Off.':
	        cols.append(f'Off_{ocount}')
	        ocount+=1
	        continue
	    cols.append(column)
	year_df.columns = cols
	# Rename columns using original index where applicable
	year_df = year_df.rename(columns={
	'PG%': 'PG_Pc',
	'SG%': 'SG_Pc',
	'SF%': 'SF_Pc',
    'PF%':'PF_Pc',
    'C%':'C_Pc',
	'OnCourt':'PMP100_OnCourt',
	'On-Off':'PMP100_On_Off',
	'BadPass': 'BadPassTO',
	'LostBall': 'LostBallTO',
	'Shoot_1': 'FoulC_Shoot',
	'Shoot_2': 'FoulD_Shoot',
	'Off_1': 'FoulC_Off',
	'Off_2': 'FoulD_Off'})
	return year_df

def shooting(site_address):
	year_df = pd.read_html(site_address, header = 1)[0]
	year_df = year_df.rename(columns={
	'FG%':'FGP',
	'Dist.': 'Dist',
	'2P':'FGAxDist_2P',
	'0-3':'FGAxDist_0_3',
	'3-10':'FGAxDist_3_10', 
	'10-16':'FGAxDist_10_16', 
	'16-3P':'FGAxDist_16_3P', 
	'3P':'FGAxDist_3P', 
	'2P.1':'FGPxDist_2P', 
	'0-3.1':'FGPxDist_0_3', 
	'3-10.1':'FGPxDist_3_10',
	'10-16.1':'FGPxDist_10_16', 
	'16-3P.1':'FGPxDist_16_3P', 
	'3P.1':'FGPxDist_3P', 
	'2P.2':'AstPc_2P', 
	'3P.2':'AstPc_3P', 
	'%FGA':'Dunks_FGA', 
	'#':'Num_Dunks', 
	'%3PA':'Corner_3PFGA',
	'3P%':'Corner_3PPc', 
	'Att.':'Heaves_Att', 
	'#.1':'Heaves_Made'})
	return year_df

def cleaner(all_df, player_ids):
	# Drop the Unnamed columns
	cols = [c for c in all_df.columns if c.lower()[:7] != 'unnamed']
	all_df = all_df[cols]
	# Get rid of additional header rows
	all_df = all_df.loc[all_df["Rk"] != "Rk"]
	all_df['PlayerID'] = player_ids
	all_df= all_df.drop_duplicates(subset=['Rk', 'Season'], keep='first')
	text_keys = ['Player','Pos','Tm', 'PlayerID']
	keys_list = all_df.keys()
	num_keys = []
	for key in keys_list:
		if key not in text_keys:
			num_keys.append(key)
	for key in num_keys:
		try:
			all_df[key] = pd.to_numeric(all_df[key])
		except:
			all_df[key] = pd.to_numeric(all_df[key].replace('%','',regex=True))/100
	from StatPuts import d_type
	if d_type == 'pergame':
		all_df = per_game(num_keys,all_df)
	elif d_type == 'per36':
		all_df = per_36(num_keys,all_df)
	all_df = all_df.fillna(0)
	player_names = all_df["Player"]
	clean_players = []
	for player in player_names:
		clean_players.append(player.replace('*', ''))
	all_df['Player'] = clean_players
	all_df = all_df.drop(columns={"Rk"})
	all_df = all_df.reset_index()
	all_df = all_df.drop(columns={'index'})
	return all_df

def per_game(num_keys, all_df):
	specials = ['Age', 'G', 'GS', 'Season']
	for key in specials:
		num_keys.remove(key)
	for key in num_keys:
		if all_df[key].dtype == 'int64':
			all_df[key] = all_df[key]/all_df['G']
			all_df[key] = all_df[key].round(1)
	return all_df


def per_36(num_keys, all_df):
	specials = ['Age', 'G', 'GS', 'MP', 'Season']
	for key in specials:
		num_keys.remove(key)
	for key in num_keys:
		if all_df[key].dtype == 'int64':
			all_df[key] = (all_df[key]/all_df['MP'])*36
			all_df[key] = all_df[key].round(1)
	return all_df


def nation():
	url = 'https://en.wikipedia.org/wiki/List_of_foreign_NBA_players'
	tables = pd.read_html(url)[6]
	tables = tables.drop(columns = ['Pos.', 'Yrs', 'Notes', 'Ref.'])
	nationality = tables['Nationality[A]'].to_list()
	birthplace = tables['Birthplace[B]'].to_list()
	country = []
	for x in range(len(nationality)):
		if birthplace[x] == '—':
			country.append(nationality[x])
		else: 
			country.append(birthplace[x])
	tables['Country'] = country
	tables = tables.drop(columns = ['Nationality[A]', 'Birthplace[B]', 'Career[C]'])
	tables=tables.replace('\\*','',regex=True)
	return tables

def final():
	stat_table = scraper()
	nation_table = nation()
	final = pd.merge(stat_table, nation_table, on = 'Player', how = 'left')
	final = final.fillna('United States')
	if os.path.exists("FlaskFiles/final.csv"):
		os.remove("FlaskFiles/final.csv")
	final.to_csv(f'FlaskFiles/final.csv')
	if os.path.exists("FlaskFiles/PlayerStats.sqlite"):
		os.remove("FlaskFiles/PlayerStats.sqlite")
	engine = create_engine('sqlite:///FlaskFiles/PlayerStats.sqlite', echo=True)
	sqlite_connection = engine.connect()
	final.to_sql('data',con=engine, index = False)
	# send data type to app
	start_year,years,garbage = search()
	from StatPuts import d_type
	table_facts = pd.DataFrame({
		'data_type':d_type,
		'start_year':start_year,
		'end_year': start_year + years - 1
	}, index=range(1))
	table_facts.to_sql('table_facts',con=engine, index = False)






