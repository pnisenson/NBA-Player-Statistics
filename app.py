from flask import Flask, render_template, redirect, request
from sqlalchemy import create_engine, func
import pandas as pd
import NBA_Scraper
import os
import time

# Create an instance of Flask
app = Flask(__name__)

# Create engine to establish SQLite connection
engine = create_engine("sqlite:///FlaskFiles/PlayerStats.sqlite", echo=True)

# Route to render index.html template using data from Mongo
@app.route("/", methods=['GET', 'POST'])
def home():
	time.sleep(2)
	df = pd.read_sql("SELECT * FROM data", con=engine, index_col = None)
	stats = df.to_html(classes="table table-striped", border=0)
	try:
		table_facts = pd.read_sql("SELECT * FROM table_facts", con=engine, index_col = None)
	except:
		table_facts = {
		'data_type': 'N/A',
		'start_year': 'N/A',
		'end_year': 'N/A'
	}
	try:
		from StatPuts import d_type,s_year,ys
		last_inputs = [d_type, s_year, str(int(s_year) + int(ys) -1)]
	except ImportError as err:
		last_inputs = ['No Input', 'No Input', 'No Input']
	except ValueError as err:
		last_inputs = ['Invalid Input', 'Invalid Input', 'Invalid Input']
	return render_template("index.html", stats=stats, last_inputs=last_inputs, table_facts=table_facts)


@app.route("/top_players")
def get_buckets():
	table_facts = pd.read_sql("SELECT * FROM table_facts", con=engine, index_col = None)
	try:
		if table_facts.data_type[0]  == 'totals' or table_facts.data_type[0]  == 'pergame' or table_facts.data_type[0]  == 'per36':
			df = pd.read_sql("SELECT Player, PTS, Season FROM data WHERE MP >= 1500 ORDER BY PTS DESC LIMIT 10", con=engine, index_col = None)
			stats = df.to_html(classes="table table-striped", border=0)
		elif table_facts.data_type[0]  == "advanced":
			df = pd.read_sql("SELECT Player, PER, Season FROM data WHERE MP >= 1500 ORDER BY PER DESC LIMIT 10", con=engine, index_col = None)
			stats = df.to_html(classes="table table-striped", border=0)
		elif table_facts.data_type[0]  == "play-by-play":
			df = pd.read_sql("SELECT Player, PMP100_On_Off, Season FROM data WHERE MP >= 1500 ORDER BY PMP100_On_Off DESC LIMIT 10", con=engine, index_col = None)
			stats = df.to_html(classes="table table-striped", border=0)	
		return render_template("second.html", stats=stats)
	except:
		return "Try a Query to determine the best player."

@app.route("/custom", methods=['GET', 'POST'])
def custom_query():
	time.sleep(2)
	try:
		from customq import query
		columns = pd.read_sql("SELECT * FROM data", con=engine, index_col = None).columns
		df = pd.read_sql(query, con=engine, index_col = None)
		stats = df.to_html(classes="table table-striped", border=0)
	except:
		stats= 'Query entered is invalid. Please build a new query'
		columns = pd.read_sql("SELECT * FROM data", con=engine, index_col = None).columns
	return render_template("custom.html", stats=stats, columns=columns)

@app.route('/inputs', methods=['GET', 'POST'])
def inputs():
	if os.path.exists("StatPuts.py"):
		os.remove("StatPuts.py")
	File_object = open(r"StatPuts.py","a")
	File_object.write(f"username = '{request.form['user']}' \n")
	File_object.write(f"password = '{request.form['pass']}' \n")
	File_object.write(f"s_year = '{request.form['start']}' \n")
	File_object.write(f"ys = '{request.form['years']}' \n")
	File_object.write(f"d_type = '{request.form['dtype']}' \n")
	return redirect("/")

@app.route('/inputstoo', methods=['GET', 'POST'])
def inputstoo():
	if os.path.exists("customq.py"):
		os.remove("customq.py")
	File_object = open(r"customq.py","a")
	if request.form['byo'] != "":
		byo = request.form['byo']
		File_object.write(f"query = '{byo}'")
	else:
		as_dict = request.form.getlist('select')
		select = ", ".join(as_dict)
		q_string = f"SELECT {select} FROM data" 
		where, order, group, limit = request.form['where'], request.form['order'], request.form['group'], request.form['limit']
		if where != "":
			q_string = f'{q_string} WHERE {where}'
		if group != "":
			q_string = f'{q_string} GROUP BY {group}'
		if order != "":
			q_string = f'{q_string} ORDER BY {order}'
		if limit != "":
			q_string = f'{q_string} LIMIT {limit}'
		File_object.write(f"query = '{q_string}'")
	return redirect("/custom")
	# return "Test"

# Route that will trigger the scrape function
@app.route("/scrape")
def scrape():
    # Run the scrape function
    nba_data = NBA_Scraper.final()

    # Redirect back to home page
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)

