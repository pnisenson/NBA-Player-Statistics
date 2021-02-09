from flask import Flask, render_template, redirect
from flask_pymongo import PyMongo
from sqlalchemy import create_engine, func
import pandas as pd
import NBA_Scraper

# Create an instance of Flask
app = Flask(__name__)

# Use PyMongo to establish Mongo connection
mongo = PyMongo(app, uri="mongodb://localhost:27017/nba_app")
engine = create_engine("sqlite:///FlaskFiles/PlayerStats.sqlite", echo=True)

# Route to render index.html template using data from Mongo
@app.route("/")
def home():
	stats = mongo.db.collection.find_one()
	return render_template("index.html", stats=stats)


@app.route("/top_players")
def get_buckets():
	#engine.execute().fetchall()
	df = pd.read_sql("SELECT Player, PER, Season FROM data WHERE MP >= 1500 ORDER BY PER DESC LIMIT 10", con=engine)
	stats = df.to_html(classes="table table-striped")
	return render_template("second.html", stats=stats)


# Route that will trigger the scrape function
@app.route("/scrape")
def scrape():

    # Run the scrape function
    nba_data = NBA_Scraper.final()

    # Find one record of data from the mongo database
    mongo.db.collection.update({}, nba_data, upsert=True)

    # Redirect back to home page
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)

