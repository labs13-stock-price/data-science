import requests
import json
from datetime import datetime


#####################
# Reddit API Scraping
#####################

def convert_unix_to_datetime(ts):
    return datetime.utcfromtimestamp(int(ts)).strftime("%Y-%m-%d %H:%M:%S")

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
    data = json.loads(r.text)
    return data["data"]


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
        before="1559347200",
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

        print(sub)
        print(len(comments))

    return comments
