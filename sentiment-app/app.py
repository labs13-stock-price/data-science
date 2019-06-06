"""
Data science Flask API endpoint.
"""

from flask import Flask, jsonify
from datetime import date, datetime, timedelta
from dateutil import parser
import os
import random
import numpy as np
import psycopg2 as pg

DBNAME = os.environ.get('DBNAME')
USER = os.environ.get('USER')
PASSWORD = os.environ.get('PASSWORD')
HOST = os.environ.get('HOST')

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
    sentiment = [round(np.random.normal(0, 0.1), 2)]
    for i in range(delta.days):
        # make sure sentiment remains between 0 and 1
        if sentiment[-1] > 0.95:
            sentiment.append(0.85)
        elif sentiment[-1] < -0.95:
            sentiment.append(-0.85)
        else:
            sentiment.append(round(sentiment[-1] + np.random.normal(0, 0.025) + -sentiment[-1] * 0.01, 2))
    return jsonify(status="success", dates=dates, sentiment=sentiment)


@app.route("/reddit/<keyword>/<start_date>/<end_date>")
def reddit_sentiment(keyword, start_date="2019-01-01", end_date="2019-05-31"):
    d2, d1 = parser.parse(end_date), parser.parse(start_date)
    delta = d2 - d1
    dates = [
        (d1 + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(delta.days + 1)
    ]

    sentiment_dict = dict.fromkeys(dates, 0.0)

    sentiment_query = """SELECT date, sentiment from sentiment
                        WHERE date BETWEEN %s and %s"""

    conn = None

    try:
        conn = pg.connect(dbname=DBNAME,
                          user=USER,
                          password=PASSWORD,
                          host=HOST)

        cursor = conn.cursor()
        cursor.execute(sentiment_query, (d1, d2))
        sentiment_records = cursor.fetchall()
        for r in sentiment_records:
            sentiment_dict[r[0].strftime("%Y-%m-%d")] = round(float(r[1]), 2)


    except (Exception, pg.DatabaseError) as error:
        print(error)
        return jsonify(status="failure", dates=dates, sentiment=None)
    finally:
        if conn is not None:
            conn.close()

    sentiment = [sentiment_dict[k] for k in sorted(sentiment_dict.keys())]

    return jsonify(status="success", dates=dates, sentiment=sentiment)

# run the app!
if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.
    app.debug = True
    app.run(host="0.0.0.0")
