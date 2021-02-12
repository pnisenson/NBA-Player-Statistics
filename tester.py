def two_returns(a, b):
	return a, b

def try_it_out():
	print(two_returns(3,4)[0])

def scraper():
	player_ids = []
	for x in range(3):
		new_ids = player_pull()
		for each_id in new_ids:
			player_ids.append(each_id)
	return player_ids

def player_pull():
	results = ['a', 'b', 'c']
	return results

print(scraper())

