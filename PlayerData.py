from selenium import webdriver
from bs4 import BeautifulSoup as bs
import pandas as pd

def login():
	from StatPuts import username, password
	login_address = 'https://stathead.com/users/login.cgi?token=1&redirect_uri=https%3A//www.basketball-reference.com/leagues/NBA_2020_totals.html'
	browser = webdriver.Chrome(executable_path=r'chromedriver.exe')
	browser.get(login_address)
	user_name = browser.find_element_by_id('username')
	user_name.send_keys(username)
	pass_word = browser.find_element_by_id('password')
	pass_word.send_keys(password)
	browser.find_element_by_id('login').submit()
	return browser

def get_all_names():
	browser = login()
	letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
	letters_c = []
	for letter in letters:
		if letter != 'X': # no players in NBA history have last name beginning with X
			letters_c.append(letter.lower())
	nametable = []
	for letter in letters_c:
		url = f'https://www.basketball-reference.com/players/{letter}/'
		browser.get(url)
		html = browser.page_source
		soup = bs(html, "html.parser")
		results = soup.find_all('th', class_='left')
		for result in results:
			try:
				if result.attrs['data-append-csv']:
					nametable.append(result.attrs['data-append-csv'])
			except:
				pass
	return nametable, browser

def get_player_data():
	get_names = get_all_names()
	playerIDList = get_names[0]
	browser = get_names[1]
	''' after the first time running, this try block will compare the old players list with
	new players list and only scrape data for the new players, saving hours of time '''
	try:
		existing_file = pd.read_csv('playerTable.csv', index_col=0)
		names_on_file = existing_file['Name'].to_list()
		while len(names_on_file) > 0:
			playerIDList.remove(names_on_file[0])
			names_on_file.remove(names_on_file[0])
	except SyntaxError:
		pass
	playerlist = []
	for player in playerIDList:
		playername = {'Name': player}
		url= f'https://www.basketball-reference.com/players/{player[0]}/{player}.html'
		browser.get(url)
		html = browser.page_source
		soup = bs(html, "html.parser")
		results = soup.find_all('span')
		strong = soup.find_all('p')
		for x in range(len(results)):
			try:
				if results[x]['itemprop'] == 'height':
					playername['Height'] = results[x].text
			except:
				continue
			try:
				if results[x]['itemprop'] == 'weight':
					playername['Weight'] = results[x].text
			except:
				continue
			try:
				if results[x]['itemprop'] == 'birthDate':
					playername['BirthDate'] = results[x]['data-birth']
			except:
				continue
			try:
				if results[x]['itemprop'] == 'birthPlace':
					playername['Country'] = results[x+1].text
					playername['State'] = results[x].contents[1].text
			except:
				continue
		for x in range(len(strong)):
			try:
				if strong[x].text.strip().split(":")[0] == 'College':
					playername['College'] = strong[x].a.text
			except:
				continue
			try:
				if strong[x].text.strip().split(":")[0] == 'Recruiting Rank':
					playername['RecruitYr'] = strong[x].text.strip().split(":")[1].split(' ')[2]
					playername['RecruitRank'] = strong[x].text.strip().split(":")[1].split(' ')[3].strip('()')
			except:
				continue
			try:
				if strong[x].text.strip().split(":")[0] == 'Draft':
					playername['DraftYear'] = strong[x].text.strip().split(',')[3].split(' ')[1]
					playername['Pick'] = strong[x].text.strip().split(',')[2].strip(')').split(' ')[1].strip("ndthsr")
			except:
				continue
		playerlist.append(playername)
		del playername
	try:
		newTable = pd.DataFrame(playerlist)
		playerTable	= pd.concat([existing_file, newTable], ignore_index=True)
	except:
		playerTable = pd.DataFrame(playerlist)
	playerTable.to_csv('playerTable.csv')


get_player_data()


