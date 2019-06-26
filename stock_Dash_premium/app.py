import dash
from dash.dependencies import Input, Output
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd

app = dash.Dash(__name__)
server = app.server

url = 'https://bz106i00uh.execute-api.us-east-2.amazonaws.com/api/'
df = pd.read_json(url).sort_values('stak score')
df = df[df.Volume > 100000]
df['stak score'] = df['stak score'].round(2)
# add an id column and set it as the index
# in this case the unique ID is just the country name, so we could have just
# renamed 'country' to 'id' (but given it the display name 'country'), but
# here it's duplicated just to show the more general pattern.
df['id'] = df['Ticker']
df.set_index('id', inplace=True, drop=False)


app.layout = html.Div([
    html.Img(src='assets/staklogo.png',width=300),
    html.H1("Interactive data table with visualizations"),
    html.P("""The stak score is composed with our proprietary\
    algorithm. It’s based on financials of the specified ticker, full history\
    risk-profile, technical analysis, and a sentiment analysis.\
    A stak score below 0 indicates a sell situation, a score above 0 is a buy.
    The stak score changes at the end of each day to reflect daily market conditions."""),
    dash_table.DataTable(
        id='datatable-row-ids',
        columns=[
            {'name': i, 'id': i, 'deletable': False} for i in df.columns
            # omit the id column
            if i != 'id'
        ],
        fixed_rows={ 'headers': True, 'data': 0 },
        style_cell={
            'whiteSpace': 'normal'
        },
        data=df.to_dict('records'),
            style_data_conditional=[
            {'if': {'column_id': 'Ticker'},
             'width': '80px'},
            {'if': {'column_id': 'Company'},
             'width': '400px'},
            {'if': {'column_id': 'Sector'},
             'width': '200px'},
            {'if': {'column_id': 'Industry'},
             'width': '200px'},
            {'if': {'column_id': 'Country'},
             'width': '100px'},
            {'if': {'column_id': 'Volume'},
             'width': '150px'},
            {'if': {'column_id': 'Price'},
             'width': '100px'},
            {'if': {'column_id': 'stak score'},
             'width': '100px'},
        ],


        filter_action='native',
        sort_action='native',
        row_selectable='multi',
        row_deletable=False,
        selected_rows=[],
        virtualization=True,
        page_action='none'
    ),
    html.Div(id='datatable-row-ids-container')
])


@app.callback(
    Output('datatable-row-ids-container', 'children'),
    [Input('datatable-row-ids', 'derived_virtual_row_ids'),
     Input('datatable-row-ids', 'selected_row_ids'),
     Input('datatable-row-ids', 'active_cell')])
def update_graphs(row_ids, selected_row_ids, active_cell):
    # When the table is first rendered, `derived_virtual_data` and
    # `derived_virtual_selected_rows` will be `None`. This is due to an
    # idiosyncracy in Dash (unsupplied properties are always None and Dash
    # calls the dependent callbacks when the component is first rendered).
    # So, if `rows` is `None`, then the component was just rendered
    # and its value will be the same as the component's dataframe.
    # Instead of setting `None` in here, you could also set
    # `derived_virtual_data=df.to_rows('dict')` when you initialize
    # the component.
    selected_id_set = set(selected_row_ids or [])

    if row_ids is None:
        dff = df
        # pandas Series works enough like a list for this to be OK
        row_ids = df['id']
    else:
        dff = df.loc[row_ids]

    active_row_id = active_cell['row_id'] if active_cell else None

    colors = ['#FF69B4' if id == active_row_id
              else '#7FDBFF' if id in selected_id_set
              else '#0074D9'
              for id in row_ids]

    return [
        dcc.Graph(
            id=column + '--row-ids',
            figure={
                'data': [
                    {
                        'x': dff['Ticker'],
                        'y': dff[column],
                        'type': 'bar',
                        'marker': {'color': colors},
                    }
                ],
                'layout': {
                    'xaxis': {'automargin': True},
                    'yaxis': {
                        'automargin': True,
                        'title': {'text': column}
                    },
                    'height': 250,
                    'margin': {'t': 10, 'l': 10, 'r': 10},
                },
            },
        )

        for column in ['stak score', 'Price', 'Volume'] if column in dff
    ]


if __name__ == '__main__':
    app.run_server(debug=True)
