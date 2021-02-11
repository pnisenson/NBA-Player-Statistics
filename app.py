from flask import Flask, render_template, redirect, request
from sqlalchemy import create_engine, func
import pandas as pd
import NBA_Scraper
import os

# Create an instance of Flask
app = Flask(__name__)

# Create engine to establish SQLite connection
engine = create_engine("sqlite:///FlaskFiles/PlayerStats.sqlite", echo=True)

# Route to render index.html template using data from Mongo
@app.route("/", methods=['GET', 'POST'])
def home():
	df = pd.read_sql("SELECT * FROM data", con=engine, index_col = None)
	stats = df.to_html(classes="table table-striped")
	try:
		from StatPuts import d_type, per
		stat_type = [d_type.lower().title() , per.lower().title()]
	except ImportError as err:
		if 'per' in ("{0}".format(err)):
			stat_type = [d_type.lower().title(), 'N/A']
		else:
			stat_type = ['Type Unknown', 'N/A']
	return render_template("index.html", stats=stats, content=df, stat_type=stat_type)


@app.route("/top_players")
def get_buckets():
	try:
		df = pd.read_sql("SELECT Player, PER, Season FROM data WHERE MP >= 1500 ORDER BY PER DESC LIMIT 10", con=engine, index_col = None)
		stats = df.to_html(classes="table table-striped")
		return render_template("second.html", stats=stats)
	except:
		df = pd.read_sql("SELECT Player, PTS, Season FROM data ORDER BY PTS DESC LIMIT 10", con=engine, index_col = None)
		stats = df.to_html(classes="table table-striped")
		return render_template("second.html", stats=stats)

@app.route("/custom")
def custom_query():
	from custom import query
	df = pd.read_sql(query, con=engine, index_col = None)
	stats = df.to_html(classes="table table-striped")
	return render_template("second.html", stats=stats)

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
	File_object.write(f"per = '{request.form['per']}' \n")
	return redirect("/")

# Route that will trigger the scrape function
@app.route("/scrape")
def scrape():
    # Run the scrape function
    nba_data = NBA_Scraper.final()

    # Redirect back to home page
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)

