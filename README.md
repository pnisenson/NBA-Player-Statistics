# NBA-Player-Statistics
# **ETL Project (Extract-Transform-Load)**

**Objective**: Analyze the impact of international players in the NBA over the past 30 years by extracting data from multiple sources, transform it, and loading it onto a database, where it can be easily accessed/queried

Deployed two data sources:	
1. Basketball-Reference.com (BKRef) 
2. Wikipedia “List_of_foreign_NBA_players” 

**Methodology**:
* Extract - Using Selenium and Splinter, scraped data from the two websites

* Transform - Deployed Pandas to clean up the data, remove special characters, and add value to the null cells. Then merged the two datasets on the player name to create comprehensive dataset including international players

* Load - Loaded the data into the SQLite database

* Querying & Visualizations - Loaded the SQLite database into Pandas and reflected the tables included using Automap database. Converted the data into a dataframe in order to plot graphs to analyze player statistics, using Matplotlib

* Flask App - We then built a flask app interface that takes all the inputs needed for scraping from the websites and automatically browses across the multiple year webpages in BKRef. The data tables are then visualized using HTML

**Usage**: 
Run app.py to run the flask app, refer to merged.ipynb for code to ETL, and Queries.ipynb for querying and visualizations

