from selenium import webdriver
import pandas as pd 
from sqlalchemy import create_engine
import os

def login(browser):
	from StatPuts import username, password
	user_name = browser.find_element_by_id('username')
	user_name.send_keys(username)
	pass_word = browser.find_element_by_id('password')
	pass_word.send_keys(password)
	browser.find_element_by_id('login').submit()
	return browser.current_url

def search():
	from StatPuts import s_year, ys, d_type
	start_year = int(s_year)
	years = int(ys)
	data_type = d_type.lower()
	return start_year,years,data_type

def scraper():
	login_address = 'https://stathead.com/users/login.cgi?token=1&redirect_uri=https%3A//www.basketball-reference.com/leagues/NBA_2020_totals.html'
	# Create Browser and set it to open the page in Chrome
	browser = webdriver.Chrome(executable_path=r'chromedriver.exe')
	browser.get(login_address)
	site_address = login(browser)
	start_year,years,data_type = search()
	browser.get(f'https://www.basketball-reference.com/leagues/NBA_{start_year}_{data_type}.html')
	files_list = []
	for x in range(1, years+1):
		site_address = browser.current_url
		year_df = pd.read_html(site_address)[0] # our data is the first table on the page
		year_df['Season'] = start_year
		year_df.to_csv(f'FlaskFiles/{start_year}{data_type}.csv') # after extracting, save to csv by year
		files_list.append(f'FlaskFiles/{start_year}{data_type}.csv') # append file name to files_list
		del year_df # delete the DataFrame from memory
		start_year += 1 # change the year to get next
		browser.get(f'https://www.basketball-reference.com/leagues/NBA_{start_year}_{data_type}.html')
	browser.quit()
	df_from_each_file = (pd.read_csv(f) for f in files_list)
	all_df = pd.concat(df_from_each_file, ignore_index=True)
	return all_df

def cleaner():
	all_df = scraper()
	# Drop the Unnamed column
	all_df = all_df.drop(columns={'Unnamed: 0'})
	# Get rid of additional header rows
	all_df = all_df.loc[all_df["Rk"] != "Rk"]
	all_df= all_df.drop_duplicates(subset=['Rk', 'Season'], keep='first')
	text_keys = ['Player','Pos','Tm']
	keys_list = all_df.keys()
	num_keys = []
	for key in keys_list:
		if key not in text_keys:
			num_keys.append(key)
	for key in num_keys:
		all_df[key] = pd.to_numeric(all_df[key])
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
	stat_table = cleaner()
	nation_table = nation()
	final = pd.merge(stat_table, nation_table, on = 'Player', how = 'left')
	final = final.fillna('United States')
	if os.path.exists("FlaskFiles/final.csv"):
		os.remove("FlaskFiles/final.csv")
	final.to_csv(f'FlaskFiles/final.csv')
	# table = final.to_html(classes="table table-striped")
	# scraped_data = {'table': table}
	if os.path.exists("FlaskFiles/PlayerStats.sqlite"):
		os.remove("FlaskFiles/PlayerStats.sqlite")
	engine = create_engine('sqlite:///FlaskFiles/PlayerStats.sqlite', echo=True)
	sqlite_connection = engine.connect()
	final.to_sql('data',con=engine, index = False)





