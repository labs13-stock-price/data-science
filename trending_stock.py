import requests
import pandas as pd
from bs4 import BeautifulSoup


def get_trending_stocks():

    url = "https://finance.yahoo.com/trending-tickers/"
    feed = requests.get(url)
    soup = BeautifulSoup(feed.text)

    fin_list = soup.find(id="yfin-list")
    f = fin_list.findAll(True, {'class': "data-col0"})

    symbol = []
    company_name = []
    for company in f:
        symbol.append(company.find('a')['data-symbol'])
        company_name.append(company.find('a')['title'])

    d = {"symbol": symbol, "company_name": company_name}
    df = pd.DataFrame(d)
    return df


print(get_trending_stocks())