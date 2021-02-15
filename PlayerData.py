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
	return browser.current_url

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
    return nametable

def get_player_data(playerIDList):
	playerlist = []
	for player in playerIDList:
	    url= f'https://www.basketball-reference.com/players/{player[0]}/{player}.html'
	    browser.get(url)
	    html = browser.page_source
	    soup = bs(html, "html.parser")
	    results = soup.find_all('span')
	    strong = soup.find_all('p')
	    for x in range(len(results)):
	        try:
	            if results[x]['itemprop'] == 'height':
	                height = results[x].text
	        except:
	            continue
	        try:
	            if results[x]['itemprop'] == 'weight':
	                weight = results[x].text
	        except:
	            continue
	        try:
	            if results[x]['itemprop'] == 'birthDate':
	                birth_date = results[x]['data-birth']
	        except:
	            continue
	        try:
	            if results[x]['itemprop'] == 'birthPlace':
	                country = results[x+1].text
	                state = results[x].contents[1].text
	        except:
	            continue
	    for x in range(len(strong)):
	        if strong[x].text.strip().split(":")[0] == 'College':
	            college = strong[x].a.text
	        if strong[x].text.strip().split(":")[0] == 'Recruiting Rank':
	            recruityr = strong[x].text.strip().split(":")[1].split(' ')[2]
	            recruitrk = strong[x].text.strip().split(":")[1].split(' ')[3].strip('()')
	        if strong[x].text.strip().split(":")[0] == 'Draft':
	            draftyr = strong[x].text.strip().split(',')[3].split(' ')[1]
	            draftpk = strong[x].text.strip().split(',')[2].strip(')').split(' ')[1].strip("ndthsr")
	    playername = {
	        'Name': player,
	        'Height':height,
	        'Weight':weight,
	        'BirthDate':birth_date,
	        'Country':country,
	        'State':state,
	        'College': college,
	        'RecruitYr': recruityr,
	        'RecruitRank':recruitrk,
	        'DraftYear':draftyr,
	        'Pick':draftpk
	    }
	    playerlist.append(playername)
	    del playername
    playerTable = pd.DataFrame(playerlist)
    playerTable.to_csv('playerTable.csv')


get_player_data(get_all_names())


