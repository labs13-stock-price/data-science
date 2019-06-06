import requests
import pandas as pd
from bs4 import BeautifulSoup


def get_trending_stocks():

    url = "https://finance.yahoo.com/trending-tickers/"
    feed = requests.get(url)
    soup = BeautifulSoup(feed.text)

    fin_list = soup.find(id="yfin-list")
    f = fin_list.findAll(True, {'class': "data-col0"})
    prices = fin_list.findAll(True, {'class': "data-col2"})

    price_list = []
    for price in prices:
        price_list.append(price.text)

    symbol = []
    company_name = []
    for company in f:
        symbol.append(company.find('a')['data-symbol'])
        company_name.append(company.find('a')['title'])

    d = {"symbol": symbol, "company_name": company_name,"price":price_list}
    df = pd.DataFrame(d)
    return d


print(get_trending_stocks())