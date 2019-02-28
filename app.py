import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html

import pandas as pd
import base64
import plotly.graph_objs as go
from plotly import tools

external_css = [ "https://cdnjs.cloudflare.com/ajax/libs/normalize/7.0.0/normalize.min.css",
        "https://cdnjs.cloudflare.com/ajax/libs/skeleton/2.0.4/skeleton.min.css",
        "//fonts.googleapis.com/css?family=Raleway:400,300,600",
        "https://codepen.io/plotly/pen/KmyPZr.css",
        "https://maxcdn.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css"]

# data post-processing
df_data = pd.read_csv('3600038_gapped.csv')

trace1 = go.Scatter(
                            x = df_data.date, 
                            y = df_data.vsolar, 
                            mode = 'lines+markers',
                            name = 'Solar Voltage',
                        )
trace2 = go.Scatter(
                            x = df_data.date, 
                            y = df_data.vbatt, 
                            mode = 'lines+markers',
                            name = 'Battery Volrage'
                        )
trace3 = go.Scatter(
                            x = df_data.date, 
                            y = df_data.degC, 
                            mode = 'lines+markers',
                            name = 'Temparature (C)'
                        )
fig = tools.make_subplots(rows=2, cols=1, specs=[[{}], [{}]],
                          shared_xaxes=True, 
                          vertical_spacing=0.1)
fig.append_trace(trace1, 2, 1)
fig.append_trace(trace2, 2, 1)
fig.append_trace(trace3, 1, 1)
fig['layout'].update()

# transmission status 

def make_dash_table( df ):
    ''' Return a dash definitio of an HTML table for a Pandas dataframe '''
    table = []
    for index, row in df.iterrows():
        html_row = []
        for i in range(len(row)):
            html_row.append( html.Td([ row[i] ]) )
        table.append( html.Tr( html_row ) )
    return table

total_num_rows = df_data.shape[0]
total_num_trans = df_data.count()['vsolar']
df_trans = pd.DataFrame({"A": ["Number of transmissions", "Percentage successful"],
        "B":[total_num_rows, total_num_trans / total_num_rows]})

# Map

mapbox_access_token = "pk.eyJ1IjoibHdhbmciLCJhIjoiY2pzbng1eGR3MGgxYzQzbXI0bjNtaWd2aiJ9.XEXULh3DR_M1a_FiSTIMdQ"

cows = [ 
        go.Scattermapbox(
            lat = df_data[df_data['clat'].notnull()]['clat'],
            lon = df_data[df_data['clng'].notnull()]['clng'],
            mode='lines+markers',
            marker=dict(size=9)
        )
    ]


cows_layout = go.Layout(
        autosize=True,
        mapbox=dict(
            accesstoken=mapbox_access_token,
            bearing=0,
            center=dict(
                lat = df_data[df_data['clat'].notnull()]['clat'].median(),
                lon = df_data[df_data['clng'].notnull()]['clng'].median()
            ),
            pitch=0,
            zoom=10,
        ),
        margin=dict(
            l=0,r=0,t=0,b=0
        )
    )
cow_fig = dict(data = cows, layout = cows_layout)
    
# generate web app
app = dash.Dash(__name__, external_stylesheets=external_css)

image_filename = 'cow.png'
encoded_image = base64.b64encode(open(image_filename, 'rb').read())

app.layout = html.Div([

    html.Div([
        
        html.Div([
            html.H5('Ceres Tag Smart Digital Ear Tag Report'),
            html.H6('James Cook University & CSIRO', style=dict(color='#7F90AC')),
        ], className = "nine columns padded" ),

        html.Div([
            html.H1('TAG'),
            html.H6([html.Span('36000', style=dict(opacity=0.5)), html.Span('38')])
        ], className = "three columns gs-header gs-accent-header padded", style=dict(float='right') ),
        
    ], className = "row gs-header gs-text-header"),

    html.Br([]),

    html.Div([

        html.Div([

            html.Img(src='data:image/png;base64,{}'.format(encoded_image)),
            html.H6('Transmission Status', className = "gs-header gs-text-header padded"),
            html.Table( make_dash_table( df_trans ) ),
            html.Div([
                dcc.Graph( 
                    id='graph',
                    figure = cow_fig
                )
            ])

        ], className = "three columns" ),

        html.Div([
            dcc.Graph(
                figure=fig
            )


        ], className = "six columns" ),

        html.Div([

            html.Label('Select Tag'),
            dcc.Dropdown(
                options = [
                    {'label': '3600038', 'value': '38'},
                    {'label': '3600049', 'value': '49'},
                    {'label': '3600057', 'value': '57'},
                    {'label': '3600063', 'value': '63'},
                    {'label': '3600065', 'value': '65'},
                    {'label': '3600072', 'value': '72'},
                    {'label': '3600076', 'value': '76'},
                    {'label': '3600077', 'value': '77'},
                    {'label': '3600080', 'value': '80'},
                ],
                value='38'
            )

        ], className = "three columns" )

    ], className = "row")

])


@app.callback(
)
if __name__ == '__main__':
    app.run_server(debug=True)
