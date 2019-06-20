import dash
from dash.dependencies import Output, Input, State
import dash_core_components as dcc
import dash_html_components as html
import plotly
import plotly.plotly as py
import plotly.graph_objs as go

import pandas_datareader.data as web
from datetime import datetime
import pandas as pd
import requests
import numpy as np
import sqlite3
from collections import Counter
import string
import regex as re
import time
import pickle
import nltk
import re
import sys
import os
import json
import base64

sys.path.insert(0, os.path.realpath(os.path.dirname(__file__)))
os.chdir(os.path.realpath(os.path.dirname(__file__)))

from cache import cache
from config import stop_words


app = dash.Dash(__name__)
server = app.server

conn = sqlite3.connect('twitter_wloc.db', check_same_thread=False)


# Get list of company names and symbols from csv
nsdq = pd.read_csv('companylist.csv')
nsdq.set_index('Symbol', inplace=True)
options = []
for tic in nsdq.index:
    options.append({'label':'{} {}'.format(tic,nsdq.loc[tic]['Name']),
                    'value':tic})

app.layout = html.Div([

    html.Div([html.H3('Select ticker symbols:'),
             dcc.Dropdown(id='my_ticker_symbol',options=options,value=['TWTR'],
                          multi=True)]),

    html.Div([html.H3('Select start and end dates:'),
             dcc.DatePickerRange(id='my_date_picker',
                                 min_date_allowed=datetime(2015, 1, 1),
                                 max_date_allowed=datetime.today(),
                                 start_date=datetime(2018, 1, 1),
                                 end_date=datetime.today())]),

    html.Div([html.Button(id='submit-button1',n_clicks=0,children='Submit')]),

    html.Div(className='row', children=[

             html.Div(dcc.Graph(id='stock-price',
                                figure={'data': [{'x': [1,2], 'y': [3,1]}]}),
                                className='col s12 m6 l6'),

            html.Div(dcc.Graph(id='risk-profile',
                               figure={'data': [{'x': [1,2], 'y': [3,1]}]}),
                               className='col s12 m6 l6')]),

    html.Div(className='row', children=[

            html.Div(dcc.Graph(id='stock-sentiment',
                               figure={'data': [{'x': [1,2], 'y': [3,1]}]}),
                               className='col s12 m6 l4'),

            html.Div([dcc.Input(id='sentiment_term', value='twitter', type='text'),
                      html.Div(['example'], id='input-div', style={'display': 'none'}),
                      html.Button('submit', id="submit-button"),
                      dcc.Graph(id='live-graph',animate=False)],
                      className='col s12 m6 l4'),

            html.Div(dcc.Graph(id='sentiment-pie', animate=False),
                     className='col s12 m6 l4')]),

    dcc.Interval(id='live-graph-update',interval=5*1000, n_intervals=0,
                 max_intervals=20),

    dcc.Interval(id='sentiment-pie-update',interval=5*1000, n_intervals=0,
                 max_intervals=20),

])


"""This callback function returns the stock price chart with candlesticks"""
@app.callback(Output('stock-price', 'figure'),
             [Input('submit-button1', 'n_clicks')],
             [State('my_ticker_symbol', 'value'),
              State('my_date_picker', 'start_date'),
              State('my_date_picker', 'end_date')])
def update_graph(n_clicks, stock_ticker, start_date, end_date):
    # Get the data and reformat it to for the pandas datareader
    start = datetime.strptime(start_date[:10], '%Y-%m-%d')
    end = datetime.strptime(end_date[:10], '%Y-%m-%d')
    traces = []
    # Pass each called stock ticker into the API, get data
    for tic in stock_ticker:
        url = f"https://hw3nhrdos1.execute-api.us-east-2.amazonaws.com/api/history/{tic}/{start}/{end}"
        df = pd.read_json(url)
        # Append each trace to a list so it can be called from n_click
        traces.append({'open':df.Open, 'high':df.High, 'low':df.Low,
                       'close':df.Close, 'x':df.index, 'y':df.Close,
                       'type':'ohlc', 'name':tic})
    fig = {
        'data': traces,
        'layout': {'title':', '.join(stock_ticker)+' Price Chart',
        'xaxis': {'rangeslider': {'visible':False}}}
    }
    return fig

"""This call back function returns the overall sentiment from Twitter"""
@app.callback(Output('stock-sentiment', 'figure'),
             [Input('submit-button1', 'n_clicks')],
             [State('my_ticker_symbol', 'value'),
              State('my_date_picker', 'start_date'),
              State('my_date_picker', 'end_date')])
def update_graph(n_clicks, stock_ticker, start_date, end_date):
    # Get the data and reformat it to for the pandas datareader
    start = datetime.strptime(start_date[:10], '%Y-%m-%d')
    end = datetime.strptime(end_date[:10], '%Y-%m-%d')
    # Function to scale the sentiment values from to -1 and 1
    def scale_range(input, min=-1, max=1):
        input += -(np.min(input))
        input /= np.max(input) / (max - min)
        input += min
        return input
    # Iterate through stock tickers & get sentiment for each on click event
    traces = []
    for tic in stock_ticker:
        url = f"http://sentiment-app.pjj2rgg23c.us-east-1.elasticbeanstalk.com\
/reddit/{tic}/{start}/{end}"
        request = requests.get(url)
        request_json = request.json()
        df_s = pd.DataFrame(request_json,columns=['dates','sentiment'])
        df_s['sentiment'] = scale_range(df_s['sentiment'].rolling(7,
                                        center=True).mean())
        traces.append({'x':df_s.dates, 'y': df_s.sentiment,
                       'line':{'color':'green', 'width':1}, 'hoverinfo':'skip'})
        traces.append({'x':df_s.dates,
                       'y':df_s.sentiment.where(df_s.sentiment >= 0),
                       'line':{'color':'green'}, 'name':'positive sentiment'})
        traces.append({'x': df_s.dates,
                       'y': df_s.sentiment.where(df_s.sentiment <= 0),
                       'line':{'color':'red'}, 'name':'negative sentiment'})
    fig = {
        'data':traces,
        'layout':{'title':', '.join(stock_ticker)+' Overall Sentiment Index',
        'showlegend':False}
    }

    return fig

"""This callback function returns the distributon
   of daily returns on a dist plot to give risk profile"""
@app.callback(Output('risk-profile', 'figure'),
             [Input('submit-button1', 'n_clicks')],
             [State('my_ticker_symbol', 'value'),
              State('my_date_picker', 'start_date'),
              State('my_date_picker', 'end_date')])
def update_graph(n_clicks, stock_ticker, start_date, end_date):
    import plotly.graph_objs as go
    start = datetime.strptime(start_date[:10], '%Y-%m-%d')
    end = datetime.strptime(end_date[:10], '%Y-%m-%d')
    traces = []
    for tic in stock_ticker:
        url = f"https://hw3nhrdos1.execute-api.us-east-2.amazonaws.com/api/history/{tic}/{start}/{end}"
        df = pd.read_json(url)
        df['Daily Pct. Change'] = (df.Close - df.Open) / df.Open
        traces.append(go.Histogram(x=df['Daily Pct. Change']\
                      .where(df['Daily Pct. Change'] < 0),
                      marker={'color':'red'}, name='negative returns')),
        traces.append(go.Histogram(x=df['Daily Pct. Change']\
                      .where(df['Daily Pct. Change'] > 0),
                      marker={'color':'green'}, name='positive returns'))

    fig = {
        'data':traces,
        'layout':{'title':', '.join(stock_ticker)+\
                  ' Risk Profile of Daily Returns',
        'showlegend':False,
        'xaxis': {'tickformat':',.2%'}}
    }
    return fig

def removeSpecialChar (raw_text):
    for k in raw_text.split("\n"):
        # Remove all special characters
        return(re.sub(r"[^a-zA-Z0-9]+", ' ', k))

MAX_DF_LENGTH = 100

def df_resample_sizes(df, maxlen=MAX_DF_LENGTH):
    df_len = len(df)
    resample_amt = 100
    vol_df = df.copy()
    vol_df['volume'] = 1

    ms_span = (df.index[-1] - df.index[0]).seconds * 1000
    rs = int(ms_span / maxlen)

    df = df.resample('{}ms'.format(int(rs))).mean()
    df.dropna(inplace=True)

    vol_df = vol_df.resample('{}ms'.format(int(rs))).sum()
    vol_df.dropna(inplace=True)

    df = df.join(vol_df['volume'])

    return df


"""This callback updates the live sentiment and pie chart div on button click"
   when the interval triggers or when the div changes"""
@app.callback(Output('input-div', 'children'),
             [Input('submit-button', 'n_clicks')],
              state=[State(component_id='sentiment_term', component_property='value')])
def update_div(n_clicks, sentiment_term):
    sentiment_term = removeSpecialChar(sentiment_term)
    return sentiment_term

"""This callback takes in data from the input-div and graph update placeholder
   to update the live sentiment graph"""
@app.callback(Output('live-graph', 'figure'),
              [Input('input-div', 'children'),
               Input('live-graph-update', 'n_intervals')])
def update_graph_scatter(sentiment_term, n_intervals):

    t17 = time.time()

    try:

        if sentiment_term:
            sql_term = "SELECT unix, sentiment FROM sentiment WHERE tweet LIKE '%"+sentiment_term+"%' ORDER BY id DESC LIMIT 800"
            df = pd.read_sql(sql_term, conn)
        else:
            df = pd.read_sql("SELECT * FROM sentiment ORDER BY id DESC, unix DESC LIMIT 800", conn)

        df.sort_values('unix', inplace=True)
        df['date'] = pd.to_datetime(df['unix'], unit='ms')
        df.set_index('date', inplace=True)
        init_length = len(df)
        df['sentiment_smoothed'] = df['sentiment'].rolling(int(len(df)/5)).mean()
        df = df_resample_sizes(df)
        X = df.index
        Y = df.sentiment_smoothed.values
        Y2 = df.volume.values
        data = plotly.graph_objs.Scatter(
                x=X,
                y=Y,
                name='Sentiment',
                mode= 'lines',
                yaxis='y2')

        data2 = plotly.graph_objs.Bar(
                x=X,
                y=Y2,
                name='Volume')

        t27 = time.time()
        print('live graph app call back bitirdim: "{}" '.format(sentiment_term), t27 - t17)

        return {'data': [data,data2],'layout' : go.Layout(xaxis=dict(range=[min(X),max(X)]),
                                                          yaxis=dict(range=[min(Y2),max(Y2*4)], title='Volume', side='right'),
                                                          yaxis2=dict(range=[min(Y),max(Y)], side='left', overlaying='y',title='sentiment'),
                                                          title='Live sentiment for: "{}"'.format(sentiment_term),
                                                          showlegend=False)}

    except Exception as e:
        with open('errors.txt','a') as f:
            f.write(str(e))
            f.write('\n')



"""This callback outputs the live pie chart"""
@app.callback(Output('sentiment-pie', 'figure'),
              [Input('input-div', 'children'),
               Input('sentiment-pie-update', 'n_intervals')])
def update_pie_chart(sentiment_term, n_intervals):
    t16 = time.time()

    sql_term = "SELECT COUNT(tweet) AS POS FROM sentiment WHERE tweet LIKE '%"+sentiment_term+"%' AND sentiment > 0.1"
    df = pd.read_sql(sql_term, conn)
    pos= df['POS'][0]
    sql_term = "SELECT COUNT(tweet) AS NEG FROM sentiment WHERE tweet LIKE '%"+sentiment_term+"%' AND sentiment < - 0.1"
    df = pd.read_sql(sql_term, conn)
    neg= df['NEG'][0]
    labels = ['Positive tweets','Negative tweets']
    values = [pos,neg]
    colors = ['green', 'red']

    trace = go.Pie(labels=labels, values=values,
                   hoverinfo='label+percent', textinfo='value',
                   marker=dict(colors=colors,line=dict(width=2)))

    t26 = time.time()
    print('setiment pie app call back bitirdim:  "{}" '.format(sentiment_term), t26 - t16)

    return {"data":[trace],'layout' : go.Layout(title=''.format(sentiment_term),
                                                showlegend=True)}


external_css = ["materialize.css"]
for css in external_css:
    app.css.append_css({"external_url": css})


if __name__ == '__main__':
    app.run_server(debug=True, port=8070) # don't forget to change the port before deploying
