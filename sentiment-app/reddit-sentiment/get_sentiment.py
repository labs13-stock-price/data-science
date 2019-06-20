import nltk

nltk.download("vader_lexicon")
from nltk.sentiment.vader import SentimentIntensityAnalyzer

import psycopg2 as pg

import time
import json
import os
import requests
from datetime import datetime
import pandas as pd
import sys

DBNAME = os.environ.get("DBNAME")
USER = os.environ.get("USER")
PASSWORD = os.environ.get("PASSWORD")
DBHOST = os.environ.get("DBHOST")


def create_table():
    """
    Creates a table for sentiment storage
    """

    conn = None

    try:
        conn = pg.connect(dbname=DBNAME, user=USER, password=PASSWORD, host=DBHOST)

        create_query = """CREATE TABLE IF NOT EXISTS sentiment(
       id serial PRIMARY KEY,
       source VARCHAR (50) NOT NULL,
       keyword VARCHAR (20) NOT NULL,
       sentiment VARCHAR (50) NOT NULL,
       date TIMESTAMP NOT NULL
        )"""

        conn.cursor().execute(create_query)

        conn.commit()

    except (Exception, pg.DatabaseError) as error:
        print(error)

    finally:
        if conn is not None:
            conn.close()


def drop_table():
    """
    Creates a table for sentiment storage
    """

    conn = None

    try:
        conn = pg.connect(dbname=DBNAME, user=USER, password=PASSWORD, host=DBHOST)

        drop_query = """DROP TABLE sentiment"""

        conn.cursor().execute(drop_query)

        conn.commit()

    except (Exception, pg.DatabaseError) as error:
        print(error)

    finally:
        if conn is not None:
            conn.close()


def insert_comments(comments, keyword):
    """
    Inserts a list of comments into Amazon RDS instance

    Args:
        - comments: dataframe where index is date and values are sentiment
        - keyword: keyword associated with sentiment (e.g. AAPL)

    Returns:
        - None
    """
    sql = """INSERT INTO sentiment(source, keyword, date, sentiment)
                 VALUES(%s, %s, %s, %s);"""
    conn = None
    try:
        # connect to the PostgreSQL database
        conn = pg.connect(dbname=DBNAME, user=USER, password=PASSWORD, host=DBHOST)
        # create a new cursor
        cur = conn.cursor()
        # execute the INSERT statement
        for i in range(len(comments.index)):

            if i == 0:
                print(comments.index[i], comments.iloc[i])

            cur.execute(sql, ("reddit", keyword, comments.index[i], comments.iloc[i]))

        # commit the changes to the database
        conn.commit()
        # close communication with the database
        cur.close()
    except (Exception, pg.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()


####################
# Sentiment Analyzer
####################

ANALYZER = SentimentIntensityAnalyzer()

# update with stock market lexicon
def stock_market_lexicon():
    """
    Creates a stock market specific lexicon for updating the Vader Sentimetn model
    """
    stock_lexicon = pd.read_csv(
        "https://raw.githubusercontent.com/jasonyip184/StockSentimentTrading/master/lexicon_data/stock_lex.csv"
    )
    stock_lexicon["sentiment"] = (
        stock_lexicon["Aff_Score"] + stock_lexicon["Neg_Score"]
    ) / 2
    stock_lexicon = dict(zip(stock_lexicon.Item, stock_lexicon.sentiment))
    stock_lexicon = {k: v for k, v in stock_lexicon.items() if len(k.split(" ")) == 1}
    stock_lexicon_scaled = {}
    for k, v in stock_lexicon.items():
        if v > 0:
            stock_lexicon_scaled[k] = v / max(stock_lexicon.values()) * 4
        else:
            stock_lexicon_scaled[k] = v / min(stock_lexicon.values()) * -4

    return stock_lexicon


ANALYZER.lexicon.update(stock_market_lexicon())

###################
# Utility functions
###################


def convert_unix_to_datetime(ts):
    return datetime.utcfromtimestamp(int(ts)).strftime("%Y-%m-%d %H:%M:%S")


#####################
# Reddit API Scraping
#####################


def get_push_shift_data(query, after, before, sub):
    """
        Gets comments for a given keyword between two dates for a single subreddit
        up to a limit of 1000

        Args:
            - query: keyword to search for
            - after: start search date as a unix timestamp
            - before: end search date as a unix timestamp
            - sub: subreddit to search

        Returns:
            - json response of search query
    """
    url = (
        "https://api.pushshift.io/reddit/search/comment/?q="
        + str(query)
        + "&size=1000&after="
        + str(after)
        + "&before="
        + str(before)
        + "&subreddit="
        + str(sub)
    )
    r = requests.get(url)
    try:
        data = json.loads(r.text)
        return data["data"]
    except json.decoder.JSONDecodeError as e:
        return []


def timestamp_to_date(ts):
    return datetime.utcfromtimestamp(ts).date()


def collect_sub_data(submission):
    """
    Parses a reddit submission for text and timestamp

    Args:
        - submission: json formatted reddit submission

    Returns:
        - tuple: (comment_text, timestamp)
    """
    try:
        return submission["body"], timestamp_to_date(submission["created_utc"])
    except KeyError:
        return "", timestamp_to_date(submission["created_utc"])


def get_all_push_shift_data(
    query,
    after="1451606400",
    before="1560459534",
    subs=["stocks", "wallstreetbets", "Trading", "investing"],
):

    """
    Gets comments for a given keyword between two dates

    Args:
        - query: keyword to search for
        - after: start search date as a unix timestamp
        - before: end search date as a unix timestamp
        - subs: list of subreddits to search

    Returns:
        - list of tuples containing (comment_text, comment_timestamp)
    """

    print("Gathering data for ticker " + query)
    print("Starting date:", convert_unix_to_datetime(after))
    print("Ending date:", convert_unix_to_datetime(before))

    comments = []

    for sub in subs:
        data = get_push_shift_data(query, after, before, sub)
        # Will run until all posts have been gathered
        # from the 'after' date up until before date
        while len(data) > 0:
            for submission in data:
                comments.append(collect_sub_data(submission))

            after_iter = data[-1]["created_utc"]
            data = get_push_shift_data(query, after_iter, before, sub)

        print(len(comments), "found in ", sub)

    return comments


def group_comments_by_date(comments):
    """
    Groups a list of comments by date
    Args:
        - comments: list of tuples (text, date)

    Returns:
        - dataframe where index is date and values are mean sentiment by date
    """

    df = pd.DataFrame(
        {
            "date": [c[1] for c in comments],
            "sentiment": [ANALYZER.polarity_scores(c[0])["compound"] for c in comments],
        }
    )
    df_by_date = df.groupby(by="date").mean()

    return df_by_date["sentiment"]


if __name__ == "__main__":
    # create databse table
    drop_table()
    create_table()

    # get companies
    df_companies = pd.read_csv("companylist.csv")
    companies = list(df_companies["Symbol"])

    for company in companies:
        # get Reddit data
        query = company
        if company == "HAS":
            query = "$HAS"
        if company == "COST":
            query = "$COST"
        if company == "GT":
            query = "$GT"
        if company == "ON":
            query = "$ON"

        args = sys.argv
        comments = get_all_push_shift_data(query=query)
        print("Total Comments", len(comments))
        if len(comments) > 0:
            comments = group_comments_by_date(comments)
            # populate table
            insert_comments(comments, keyword=company)
