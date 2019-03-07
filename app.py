import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html

import pandas as pd
import base64
import plotly.graph_objs as go
from plotly import tools
import datetime
import urllib.request

external_css = [ "https://cdnjs.cloudflare.com/ajax/libs/normalize/7.0.0/normalize.min.css",
        "https://cdnjs.cloudflare.com/ajax/libs/skeleton/2.0.4/skeleton.min.css",
        "//fonts.googleapis.com/css?family=Raleway:400,300,600",
        "https://codepen.io/plotly/pen/KmyPZr.css",
        "https://maxcdn.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css"]

today = datetime.datetime.today()

def create_time_series(df_time):
    trace1 = go.Scatter(
                            x = df_time.date, 
                            y = df_time.vsolar, 
                            mode = 'lines+markers',
                        )
    trace2 = go.Scatter(
                            x = df_time.date, 
                            y = df_time.vbatt, 
                            mode = 'lines+markers',
                        )
    trace3 = go.Scatter(
                            x = df_time.date, 
                            y = df_time.degC, 
                            mode = 'lines+markers',
                        )
    trace4 = go.Scatter(
                            x = df_time.date, 
                            y = df_time.Δd, 
                            mode = 'lines+markers',
                        )
    fig = tools.make_subplots(rows=4, cols=1, specs=[[{}], [{}], [{}], [{}]],
                          shared_xaxes=True, 
                          vertical_spacing=0.1)

    fig.append_trace(trace1, 4, 1)
    fig.append_trace(trace2, 3, 1)
    fig.append_trace(trace3, 2, 1)
    fig.append_trace(trace4, 1, 1)

    fig['layout']['yaxis1'].update(title='Solar Valtage')
    fig['layout']['yaxis2'].update(title='Battery Valtage')
    fig['layout']['yaxis3'].update(title='Temparature (C)')
    fig['layout']['yaxis4'].update(title=r'$\Delta$ Distance (m)')

    fig['layout'].update(showlegend=False, height=800)

    return fig

# transmission status 

def create_dash_table( df ):
    ''' Return a dash definitio of an HTML table for a Pandas dataframe '''
    table = []
    for index, row in df.iterrows():
        html_row = []
        for i in range(len(row)):
            html_row.append( html.Td([ row[i] ]) )
        table.append( html.Tr( html_row ) )
    return table


# Map
def create_map(df_map, zoom, bearing):
    f_token = open('token_key.txt', 'r')
    token_key = f_token.read()
    mapbox_access_token = token_key

    cows = [ 
            go.Scattermapbox(
                lat = df_map[df_map['clat'].notnull()]['clat'],
                lon = df_map[df_map['clng'].notnull()]['clng'],
                mode='lines+markers',
                marker=dict(size=9)
            )
        ]

    cows_layout = go.Layout(
            autosize=True,
            mapbox=dict(
                accesstoken=mapbox_access_token,
                bearing=bearing,
                center=dict(
                    lat = df_map[df_map['clat'].notnull()]['clat'].median(),
                    lon = df_map[df_map['clng'].notnull()]['clng'].median()
                ),
                zoom=zoom,
            ),
            margin=dict(
                l=0,r=0,t=0,b=0
            ),
        )
    cow_fig = dict(data = cows, layout = cows_layout)
    return cow_fig
    
# generate web app
app = dash.Dash(__name__, external_stylesheets=external_css)

#image_filename = 'cow.png'
#encoded_image = base64.b64encode(open(image_filename, 'rb').read())

app.layout = html.Div([

    html.Div([
        
        html.Div([
            html.H4('Ceres Tag Smart Digital Ear Tag Report'),
            html.H5('James Cook University & CSIRO', style=dict(color='#7F90AC')),
        ], className = "nine columns padded" ),

        html.Div([
            html.H1('TAG'),
            html.H5([html.Span('36000', style=dict(opacity=0.5)), html.Span(id='tag-id')])
        ], className = "three columns gs-header gs-accent-header padded", style=dict(float='right') ),
        
    ], className = "row gs-header gs-text-header"),

    html.Br([]),

    html.Div([

        html.Div([

            html.Img(id = 'cow-img'),

        ], className = "four columns" ),

        html.Div([

            html.Div([
                dcc.Graph( 
                    id='map-track',
                )
            ])

        ], className = "four columns" ),

        html.Div([

            html.H5('Control Panel', className = "gs-header gs-text-header padded"),
            html.Label('Select Tag', style={'fontSize': 15}),
            dcc.Dropdown(
                id='dropdown-tag',
                options = [
                    {'label': '3600038', 'value': '3600038'},
                    {'label': '3600049', 'value': '3600049'},
                    {'label': '3600057', 'value': '3600057'},
                    {'label': '3600063', 'value': '3600063'},
                    {'label': '3600065', 'value': '3600065'},
                    {'label': '3600072', 'value': '3600072'},
                    {'label': '3600076', 'value': '3600076'},
                    {'label': '3600077', 'value': '3600077'},
                    {'label': '3600080', 'value': '3600080'},
                ],
                value='3600038',
                style={'fontSize': 15}
            ),

            html.Label('Start time (YYYY-MM-DD HH:MM:SS)', style={'fontSize': 15}),
            dcc.Input(id='start-time', 
                      value='2019-02-16 12:00:00', 
                      type='text', 
                      style={'fontSize': 15}),
            html.Label('End time (YYYY-MM-DD HH:MM:SS)', style={'fontSize': 15}),
            dcc.Input(id='end-time', value=str(today.year) + '-'
                                          +str(today.month) + '-'
                                          +str(today.day) + ' '
                                          +str(today.hour) + ':'
                                          +str(today.minute) + ':'
                                          +str(today.second), 
                      type='text',
                      style={'fontSize': 15}),

            html.H5('Transmission Status', className = "gs-header gs-text-header padded"),
            html.Table(id='transmission', style={'fontSize': 15}),

        ], className = "four columns" )

    ], className = "row"),

    html.Br([]),

    html.Div([

        html.Div([
            dcc.Graph(
                id='time-series'
            )


        ], className = "twelve columns" ),

    ], className = "row"),
])


@app.callback(
        Output("cow-img", "src"),
        [Input("dropdown-tag", "value")]
)
def update_cow_image(tag_id):
    return app.get_asset_url('cow_3600038.png')

@app.callback(
        Output('map-track', 'figure'),
        [Input('dropdown-tag', 'value'),
         Input('start-time', 'value'),
         Input('end-time', 'value')],
        [State('map-track', 'relayoutData')]
)
def update_map(tag_id, start_date, end_date, prevLayout):
    url = 'https://digitalhomestead.hpc.jcu.edu.au/ct/' + tag_id +'_gapped.csv'
    urllib.request.urlretrieve(url, './' + tag_id + '_gapped.csv')
    csv_filename = tag_id + '_gapped.csv'
    df_full = pd.read_csv(csv_filename)
    mask = (df_full['date'] > start_date) & (df_full['date'] < end_date)
    df_full = df_full.loc[mask]
    #if prevLayout is not None:
    #    zoom = float(prevLayout['mapbox']['zoom'])
    #    bearing = float(prevLayout['mapbox']['bearing'])
    #else:
    #    zoom = 12
    #    bearing = 0
    zoom = 12
    bearing = 0
    return create_map(df_full, zoom, bearing)

@app.callback(
        Output('time-series', 'figure'),
        [Input('dropdown-tag', 'value'),
         Input('start-time', 'value'),
         Input('end-time', 'value')]
)
def update_time_series(tag_id, start_date, end_date):
    url = 'https://digitalhomestead.hpc.jcu.edu.au/ct/' + tag_id +'_gapped.csv'
    urllib.request.urlretrieve(url, './' + tag_id + '_gapped.csv')
    csv_filename = tag_id + '_gapped.csv'
    df_full = pd.read_csv(csv_filename)
    mask = (df_full['date'] > start_date) & (df_full['date'] < end_date)
    df_full = df_full.loc[mask]
    return create_time_series(df_full)

@app.callback(
        Output('transmission', 'children'),
        [Input('dropdown-tag', 'value'),
         Input('start-time', 'value'),
         Input('end-time', 'value')]
)
def update_trans_table(tag_id, start_date, end_date):
    url = 'https://digitalhomestead.hpc.jcu.edu.au/ct/' + tag_id +'_gapped.csv'
    urllib.request.urlretrieve(url, './' + tag_id + '_gapped.csv')
    csv_filename = tag_id + '_gapped.csv'
    df_full = pd.read_csv(csv_filename)
    mask = (df_full['date'] > start_date) & (df_full['date'] < end_date)
    df_full = df_full.loc[mask]
    total_num_rows = df_full.shape[0]
    total_num_trans = df_full.count()['vsolar']
    df_trans = pd.DataFrame({"A": ["Number of transmissions", "Percentage successful"],
        "B":[total_num_rows, "{0:.2f}%".format(100*total_num_trans / total_num_rows)]})
    return create_dash_table(df_trans)

@app.callback(
        Output('tag-id', 'children'),
        [Input('dropdown-tag', 'value')]
)
def update_tag_id(tag_id):
    return tag_id[-2:]


if __name__ == '__main__':
    app.run_server(debug=True)
