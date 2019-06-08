import os
import sys
sys.path.insert(0, os.path.realpath(os.path.dirname(__file__)))
os.chdir(os.path.realpath(os.path.dirname(__file__)))

from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener
import json
import sqlite3
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from unidecode import unidecode
import time
from threading import Lock, Timer
import pandas as pd
from config import stop_words
import regex as re
from collections import Counter
import string
import pickle
import itertools
from textblob import TextBlob
import datetime

analyzer = SentimentIntensityAnalyzer()

# Twitter keys
ckey = '1wKYaitEhrElIXVsZKXxyePfW'
csecret = '5sSg4Kgqk2r5O4d5XxqFiim4gWt6dOiHnJVGlm9wzZt1daqjlP'
atoken = '1082776925767122944-hcaROCH3H2tP8K9rHC1vgxYImf6rm5'
asecret = 'fbPhtbtpq1PEK86srvlBwDB6gZGgPfrYboKpJ3aRHUAp7'

"""Isolation lever disables automatic transactions, we are disabling thread
   check as we are creating connection here, but we'll be inserting from a
   separate thread (no need for serialization)"""

conn = sqlite3.connect('twitter_wloc.db', isolation_level=None, check_same_thread=False)
c = conn.cursor()



us_state_abbrev = {
        'AK': 'Alaska',
        'AL': 'Alabama',
        'AR': 'Arkansas',
        'AZ': 'Arizona',
        'CA': 'California',
        'CO': 'Colorado',
        'CT': 'Connecticut',
        'DC': 'District of Columbia',
        'DE': 'Delaware',
        'FL': 'Florida',
        'GA': 'Georgia',
        'HI': 'Hawaii',
        'IA': 'Iowa',
        'ID': 'Idaho',
        'IL': 'Illinois',
        'IN': 'Indiana',
        'KS': 'Kansas',
        'KY': 'Kentucky',
        'LA': 'Louisiana',
        'MA': 'Massachusetts',
        'MD': 'Maryland',
        'ME': 'Maine',
        'MI': 'Michigan',
        'MN': 'Minnesota',
        'MO': 'Missouri',
        'MS': 'Mississippi',
        'MT': 'Montana',
        'NC': 'North Carolina',
        'ND': 'North Dakota',
        'NE': 'Nebraska',
        'NH': 'New Hampshire',
        'NJ': 'New Jersey',
        'NM': 'New Mexico',
        'NV': 'Nevada',
        'NY': 'New York',
        'OH': 'Ohio',
        'OK': 'Oklahoma',
        'OR': 'Oregon',
        'PA': 'Pennsylvania',
        'RI': 'Rhode Island',
        'SC': 'South Carolina',
        'SD': 'South Dakota',
        'TN': 'Tennessee',
        'TX': 'Texas',
        'UT': 'Utah',
        'VA': 'Virginia',
        'VT': 'Vermont',
        'WA': 'Washington',
        'WI': 'Wisconsin',
        'WV': 'West Virginia',
        'WY': 'Wyoming'
}

#search the location string for a long form state name. If found, abbreviate into state code.
def update_state (loc, us_state_abbrev):
    state_abbrev = ''
    for key, value in us_state_abbrev.items():
        #print (value)
        if value.upper() in loc.upper():
            state_abbrev = key
            #print ('new state code is: ', state_abbrev)
            return state_abbrev

def create_table():
    try:
        # http://www.sqlite.org/pragma.html#pragma_journal_mode
        # for us - it allows concurrent write and reads
        c.execute("PRAGMA journal_mode=wal")
        c.execute("PRAGMA wal_checkpoint=TRUNCATE")
        c.execute("PRAGMA auto_vacuum = INCREMENTAL")
        c.execute("PRAGMA main.incremental_vacuum")

        # changed unix to INTEGER (it is integer, sqlite can use up to 8-byte long integers)
        c.execute("CREATE TABLE IF NOT EXISTS sentiment(id INTEGER PRIMARY KEY AUTOINCREMENT, unix INTEGER, tweet TEXT, loc VARCHAR, state_code VARCHAR, city_name TEXT, country TEXT, followers_count INTEGER, sentiment REAL)")
        # key-value table for random stuff
        c.execute("CREATE TABLE IF NOT EXISTS misc(key TEXT PRIMARY KEY, value TEXT)")
        # US states sentiment summary tabe
        c.execute("CREATE TABLE IF NOT EXISTS states(state_code VARCHAR PRIMARY KEY, sentiment REAL, nb_tweets INTEGER)")
        # id on index, both as DESC (as you are sorting in DESC order)
        c.execute("CREATE INDEX id_unix ON sentiment (id DESC, unix DESC)")
        # out full-text search table, i choosed creating data from external (content) table - sentiment
        # instead of directly inserting to that table, as we are saving more data than just text
        # https://sqlite.org/fts5.html - 4.4.2
        #c.execute("CREATE VIRTUAL TABLE sentiment_fts USING fts5(tweet, content=sentiment, content_rowid=id, prefix=1, prefix=2, prefix=3)")
        # that trigger will automagically update out table when row is inserted
        # (requires additional triggers on update and delete)
        #c.execute(
        #    CREATE TRIGGER sentiment_insert AFTER INSERT ON sentiment BEGIN
        #        INSERT INTO sentiment_fts(rowid, tweet) VALUES (new.id, new.tweet);
        #    END
        #        )
    except Exception as e:
        print(str(e))
create_table()

# create lock
lock = Lock()

# states  source : https://github.com/KobaKhit/sixopy/blob/master/sixopy/tw.py
states = ['AK', 'AL', 'AR', 'AZ', 'CA', 'CO', 'CT', 'DC', 'DE', 'FL', 'GA', 'HI', 'IA', 'ID', 'IL', 'IN', 'KS', 'KY', 'LA', 'MA', 'MD', 'ME', 'MI', 'MN', 'MO', 'MS', 'MT', 'NC', 'ND', 'NE', 'NH', 'NJ', 'NM', 'NV', 'NY', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VA', 'VT', 'WA', 'WI', 'WV', 'WY']
states = [x for x in map(lambda x:x.upper(),states)]
#state and city name splitter.  source : https://github.com/KobaKhit/sixopy/blob/master/sixopy/tw.py
def get_state_city(loc):
  # extracts state and city if state is a US state
  # Args:
  #  - location - string (Phoenix, AZ)
  statecity = ['','']
  if loc != None and ',' in loc:
    loc = loc.upper()
    locsplit = loc.split(',')
    if re.sub('[\s+]', '', locsplit[1]) in states:
          statecity = [re.sub('[\s+]', '', locsplit[1]), locsplit[0]]
    elif re.sub('[\s+]', '', locsplit[0]) in states:
          statecity = [re.sub('[\s+]', '', locsplit[0]), locsplit[1]]
  return(statecity)


class listener(StreamListener):

    data = []
    lock = None

    def __init__(self, lock):

        # create lock
        self.lock = lock

        # init timer for database save
        self.save_in_database()

        # call __inint__ of super class
        super().__init__()

    def save_in_database(self):

        # set a timer (1 second)
        Timer(1, self.save_in_database).start()

        # with lock, if there's data, save in transaction using one bulk query
        with self.lock:
            if len(self.data):

                now = datetime.datetime.now()   #comment me out later on
                if now.hour == 4 and now.minute == 43 and now.second < 2.5:  #run a truncate code at every midnight at server local time. Server is 4 hours ahead of EST/NY
                    print (now.year, now.month, now.day, now.hour, now.minute, now.second)
                    # 2015 5 6 8 53 40
                    # database truncate routine. Check if this slows down the twitter stream.
                    HM_DAYS_KEEP = 2.5  #max days of history in the database
                    current_ms_time = time.time()*1000
                    one_day = 86400 * 1000
                    del_to = int(current_ms_time - (HM_DAYS_KEEP * one_day))
                    sql = "DELETE FROM sentiment WHERE unix <  '{}'".format(del_to)
                    c.execute(sql)
                    time.sleep(5)
                    # you will need to vacuum if you ever do a bulk delete.
                    sql = "VACUUM"
                    c.execute(sql)
                    time.sleep(5)
                    print('vacuumed on ', datetime.datetime.now())


                c.execute('BEGIN TRANSACTION')
                try:
                    c.executemany("INSERT INTO sentiment (unix, tweet, loc, state_code, city_name, country, followers_count, sentiment) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", self.data)
                except:
                    pass

                c.execute('COMMIT')
                self.data = []

    def on_data(self, data):
        try:
            #print(data)
            data = json.loads(data)
            # there are records like that:
            # {'limit': {'track': 14667, 'timestamp_ms': '1520216832822'}}
            if 'truncated' not in data:
                #print(data)
                return True
            if data['truncated']:
                tweet = unidecode(data['extended_tweet']['full_text'])
            else:
                tweet = unidecode(data['text'])
            time_ms = data['timestamp_ms']

            loc = (data['user']['location'])
            if loc is not None:
                state_code = get_state_city(data["user"]["location"])[0]    #update with cleaned up state code like CA, OH, FL
                city_name = get_state_city(data["user"]["location"])[1]    #update with long form city name
            else:
                state_code = ''
                city_name = ''

            #update loc with the US state abrev from the location free text. If the state name exists than abbrev into state_code
            if loc is not None and state_code == '':
                state_code = update_state(loc, us_state_abbrev)
                #print('new updated state code is: ', state_code)


            if data['place'] is not None:
                country = data['place']   #update with available place info. Though there is place attribute filled in. Maybe change this with coordinates based in the future.
            else:
                country = ''

            followers_count  = (data['user']['followers_count'])
            vs = analyzer.polarity_scores(tweet)
            sentiment = vs['compound']
            #print(time_ms, tweet, sentiment)

            # append to data list (to be saved every 1 second)
            with self.lock:
                self.data.append((time_ms, tweet, loc, state_code, city_name, country, followers_count, sentiment))

        except KeyError as e:
            print('There is a KeyError.')
            print(str(e))
        return True

    def on_error(self, status_code):
        print(status_code, 'There is a twitter api on error code triggred. I will sleep a bit and then restart.')
        time.sleep(60)
        return False # To continue listening



def map_nouns(col):
    return [word[0] for word in TextBlob(col).tags if word[1] == u'NNP']

# make a counter with blacklist words and empty word with some big value - we'll use it later to filter counter
stop_words.append('')
blacklist_counter = Counter(dict(zip(stop_words, [1000000] * len(stop_words))))

# compile a regex for split operations (punctuation list, plus space and new line)
punctuation = [str(i) for i in string.punctuation]
split_regex = re.compile("[ \n" + re.escape("".join(punctuation)) + ']')


while True:   #infinite while loop to listen Twitter API

    try:
        auth = OAuthHandler(ckey, csecret)
        auth.set_access_token(atoken, asecret)
        twitterStream = Stream(auth, listener(lock))

        # LOCATIONS are the longitude, latitude coordinate corners for a box that restricts the
        # geographic area from which you will stream tweets. The first two define the southwest
        # corner of the box and the second two define the northeast corner of the box.
        #LOCATIONS = [-124.7771694, 24.520833, -66.947028, 49.384472,        # Contiguous US
        #             -164.639405, 58.806859, -144.152365, 71.76871,         # Alaska
        #             -160.161542, 18.776344, -154.641396, 22.878623]        # Hawaii

        twitterStream.filter(track=["t"], languages=["en"])      # locations=LOCATIONS
        #twitterStream.filter(stall_warnings=True)

    except Exception as e:
        print('exception at...', datetime.datetime.now())
        print(str(e), "There is an exception with twitter stream!")
        time.sleep(5)
