import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

import pandas_datareader.data as web
from datetime import datetime
import pandas as pd
import requests
import numpy as np


app = dash.Dash(__name__)
server = app.server

# Get list of company names and symbols from csv
nsdq = pd.read_csv('companylist.csv')
nsdq.set_index('Symbol', inplace=True)
options = []
for tic in nsdq.index:
    options.append({'label':'{} {}'.format(tic,nsdq.loc[tic]['Name']),
                    'value':tic})

xs = np.linspace(0, 20, 100)
ys = np.sin(xs) + xs*0.1
df = pd.DataFrame({'x': xs, 'y': ys})

app.layout = html.Div([
    html.H1('Stock Market Analytics'),
    html.Div([
        html.H3('Select ticker symbols:', style={'paddingRight':'30px'}),
        dcc.Dropdown(
            id='my_ticker_symbol',
            options=options,
            value=['SPY'],
            multi=True
        )
    ], style={'display':'inline-block', 'verticalAlign':'top', 'width':'30%'}),
    html.Div([
        html.H3('Select start and end dates:'),
        dcc.DatePickerRange(
            id='my_date_picker',
            min_date_allowed=datetime(2015, 1, 1),
            max_date_allowed=datetime.today(),
            start_date=datetime(2018, 1, 1),
            end_date=datetime.today()
        )
    ], style={'display':'inline-block'}),
    html.Div([
        html.Button(
            id='submit-button',
            n_clicks=0,
            children='Submit',
            style={'fontSize':20, 'marginLeft':'20px'}
        ),
    ], style={'display':'inline-block'}),
    dcc.Graph(
        id='stock-price',
        figure={
            'data': [
                {'x': [1,2], 'y': [3,1]}
            ]
        }
    ),
    dcc.Graph(
        id='stock-sentiment',
        figure={
            'data': [
                {'x': [1,2], 'y': [3,1]}
            ]
        }
    ),
    dcc.Graph(
        id='stock-returns',
        figure={
            'data': [
                {'x': [1,2], 'y': [3,1]}
            ]
        }
    ),
    # # Graph for testing
    # dcc.Graph(
    #     id='xyz',
    #     figure={
    #         'data': [
    #             {'x': xs, 'y': df.y, 'line':{'color':'black'}},
    #             {'x': xs, 'y': df.y.where(df.y <= 1), 'line':{'color':'green'}}
    #         ]
    #     }
    # )
])


"""This callback function returns the stock price chart with candlesticks"""
@app.callback(Output('stock-price', 'figure'),
             [Input('submit-button', 'n_clicks')],
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
        df = web.DataReader(tic,'iex',start,end)
        # Append each trace to a list so it can be called from n_click
        traces.append({'open':df.open, 'high':df.high, 'low':df.low,
                       'close':df.close, 'x':df.index, 'y':df.close,
                       'type':'candlestick', 'name':tic})
    fig = {
        'data': traces,
        'layout': {'title':', '.join(stock_ticker)+' Price Chart',
        'xaxis': {'rangeslider': {'visible':False}}}
    }
    return fig

"""Call back function returns the stock sentiment
   chart from Twitter sentiment"""
@app.callback(Output('stock-sentiment', 'figure'),
             [Input('submit-button', 'n_clicks')],
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
/test/{tic}/{start}/{end}"
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
        'layout':{'title':', '.join(stock_ticker)+' Twitter Sentiment Index',
        'showlegend':False}
    }

    return fig

"""This callback function returns the distributon
   of daily returns on a dist to give risk profile"""
@app.callback(Output('stock-returns', 'figure'),
             [Input('submit-button', 'n_clicks')],
             [State('my_ticker_symbol', 'value'),
              State('my_date_picker', 'start_date'),
              State('my_date_picker', 'end_date')])
def update_graph(n_clicks, stock_ticker, start_date, end_date):
    import plotly.graph_objs as go
    start = datetime.strptime(start_date[:10], '%Y-%m-%d')
    end = datetime.strptime(end_date[:10], '%Y-%m-%d')
    traces = []
    for tic in stock_ticker:
        df = web.DataReader(tic,'iex',start,end)
        df['Daily Pct. Change'] = (df.close - df.open) / df.open
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


if __name__ == '__main__':
    app.run_server(debug=True)
