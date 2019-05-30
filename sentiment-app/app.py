"""
Data science Flask API endpoint.
"""

from flask import Flask, jsonify
from datetime import date, datetime, timedelta
from dateutil import parser
import os
import random

# TODO setup env vars to connect to Amazon RDS database

# EB looks for an 'application' callable by default.
app = Flask(__name__)


@app.route("/")
def hello_world():
    """
    A function to make sure the app is running during initial testing
    """
    return "Hello world!"


@app.route("/test/<keyword>/<start_date>/<end_date>")
def test_sentiment(keyword="", start_date="2019-01-01", end_date="2019-05-31"):
    """
    Test route for front end to use during development

    Args:
        - keyword (str, optional): keyword for which sentiment analysis will be returned
        - start_date (str, optional): start date of sentiment analysis
        - end_date (str, optional): end date of sentiment analysis

    Returns:
        - json with status, sentiment, and list of dates
    """
    d2, d1 = parser.parse(end_date), parser.parse(start_date)
    delta = d2 - d1
    dates = [
        (d1 + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(delta.days + 1)
    ]
    sentiment = [round(random.uniform(-1.0, 1.0), 2) for _ in range(delta.days + 1)]
    return jsonify(status="success", dates=dates, sentiment=sentiment)


# run the app!
if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.
    app.debug = True
    app.run(host="0.0.0.0")
