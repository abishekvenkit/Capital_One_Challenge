from flask import Flask, render_template
from flask_bootstrap import Bootstrap
import csv
import matplotlib.pyplot as plt, mpld3
import matplotlib.cm
import json
from haversine import haversine
import math
import numpy as np
import seaborn as sns
import pandas as pd

from graphs import *

#create app (uses bootstrap template)
app = Flask(__name__)
Bootstrap(app)

#create routes with respective template files
@app.route("/")
def home_page():
	return render_template("home.html")

@app.route("/data_visuals")
def data_visuals():
	return render_template("data_visuals.html")

# @app.route("/location_analysis")
# def location_analysis():
# 	return render_template("popular_locs_map.html")

# @app.route("/distance_riders")
# def distance_riders():
# 	return render_template("distance_riders.html")

# @app.route("/seasons")
# def seasons():
# 	return render_template("seasons.html")

# @app.route("/bike_logistics")
# def bike_logistics():
# 	return render_template("bike_logistics.html")

# @app.route("/category_passholder")
# def category_passholder():
# 	return render_template("category_passholder.html")

if __name__ == "__main__":
    app.run()